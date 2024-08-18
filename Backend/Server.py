from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from flask_bcrypt import Bcrypt
import uuid
import jwt
import datetime
from functools import wraps
import secrets
#forgot password testing
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pytz
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)
bcrypt = Bcrypt(app)

app.config['SECRET_KEY'] = secrets.token_hex(32)  # Change this to a secure random key

# MySQL Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="user_authentication"
)

cursor = db.cursor(dictionary=True)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "No token provided"}), 401
        try:
            token = token.split()[1]  # Remove 'Bearer ' prefix
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return jsonify({"error": "Invalid token"}), 401
        return f(data['user_id'], *args, **kwargs)
    return decorated

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data['email']
    phone_number = data['phone_number']
    password = data['password']

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    try:
        cursor.execute("INSERT INTO users (email, phone_number, password_hash) VALUES (%s, %s, %s)", (email, phone_number, password_hash))
        db.commit()
        return jsonify({"message": "User registered successfully!"}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']

        cursor.execute("SELECT id, password_hash FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()

        if result and bcrypt.check_password_hash(result['password_hash'], password):
            token = jwt.encode(
                {
                    'user_id': result['id'],
                    'exp': datetime.now(pytz.UTC) + timedelta(hours=24)
                },
                app.config['SECRET_KEY'],
                algorithm='HS256'  # Specify the algorithm
            )
            return jsonify({"message": "Login successful!", "token": token, "user_id": result['id']}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# @app.route('/login', methods=['POST'])
# def login():
#     try:
#         data = request.get_json()
#         email = data['email']
#         password = data['password']

#         cursor.execute("SELECT id, password_hash FROM users WHERE email = %s", (email,))
#         result = cursor.fetchone()

#         if result and bcrypt.check_password_hash(result['password_hash'], password):
#             token = jwt.encode(
#                 {
#                     'user_id': result['id'],
#                     'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=24)
#                 },
#                 app.config['SECRET_KEY'],
#                 algorithm='HS256'  # Specify the algorithm
#             )
#             return jsonify({"message": "Login successful!", "token": token, "user_id": result['id']}), 200
#         else:
#             return jsonify({"error": "Invalid credentials"}), 401
#     except Exception as e:
#         print(f"Error occurred: {e}")
#         return jsonify({"error": "Internal Server Error"}), 500

@app.route('/verify_token', methods=['GET'])
def verify_token():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "No token provided"}), 401
    try:
        token = token.split()[1]  # Remove 'Bearer ' prefix
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        return jsonify({"valid": True, "user_id": data['user_id']}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

#Invitation acceptance admin powers to creator of group
@app.route('/create_family_group', methods=['POST'])  #new code for creating group
@token_required
def create_family_group(user_id):
    data = request.get_json()
    group_name = data['group_name']
    
    group_id = str(uuid.uuid4())
    
    try:
        cursor.execute("INSERT INTO family_groups (id, name, creator_id) VALUES (%s, %s, %s)", (group_id, group_name, user_id))
        cursor.execute("UPDATE users SET group_id = %s WHERE id = %s", (group_id, user_id))
        db.commit()
        return jsonify({"message": "Family group created successfully!", "group_id": group_id}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400
    
@app.route('/get_group_members', methods=['GET'])
@token_required
def get_group_members(user_id):
    try:
        cursor.execute("SELECT group_id FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        if not result or not result['group_id']:
            return jsonify({"error": "User is not in a group"}), 400

        group_id = result['group_id']

        cursor.execute("""
            SELECT u.id, u.email, u.phone_number, fg.creator_id
            FROM users u
            JOIN family_groups fg ON u.group_id = fg.id
            WHERE u.group_id = %s
        """, (group_id,))
        members = cursor.fetchall()

        is_creator = any(member['id'] == user_id and member['id'] == member['creator_id'] for member in members)

        return jsonify({
            "members": members,
            "is_creator": is_creator
        }), 200
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400
    
@app.route('/remove_group_member', methods=['POST'])
@token_required
def remove_group_member(user_id):
    data = request.get_json()
    member_id = data['member_id']
    
    try:
        cursor.execute("SELECT group_id FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        if not result or not result['group_id']:
            return jsonify({"error": "User is not in a group"}), 400

        group_id = result['group_id']

        cursor.execute("SELECT creator_id FROM family_groups WHERE id = %s", (group_id,))
        result = cursor.fetchone()
        if result['creator_id'] != user_id:
            return jsonify({"error": "Only the group creator can remove members"}), 403

        cursor.execute("UPDATE users SET group_id = NULL WHERE id = %s AND group_id = %s", (member_id, group_id))
        db.commit()

        return jsonify({"message": "Member removed successfully"}), 200
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400
    
@app.route('/delete_group', methods=['POST'])
@token_required
def delete_group(user_id):
    try:
        # First, get the user's group_id
        cursor.execute("SELECT group_id FROM users WHERE id = %s", (user_id,))
        user_result = cursor.fetchone()
        if not user_result or not user_result['group_id']:
            return jsonify({"error": "User is not in a group"}), 400

        group_id = user_result['group_id']

        # Check if the user is the creator of the group
        cursor.execute("SELECT creator_id FROM family_groups WHERE id = %s", (group_id,))
        group_result = cursor.fetchone()
        if not group_result or group_result['creator_id'] != user_id:
            return jsonify({"error": "Only the group creator can delete the group"}), 403

        # Start a transaction
        cursor.execute("START TRANSACTION")

        # Delete invitations associated with this group
        cursor.execute("DELETE FROM invitations WHERE group_id = %s", (group_id,))

        # Update users to remove them from the group
        cursor.execute("UPDATE users SET group_id = NULL WHERE group_id = %s", (group_id,))

        # Delete the group
        cursor.execute("DELETE FROM family_groups WHERE id = %s", (group_id,))

        # Commit the transaction
        db.commit()

        return jsonify({"message": "Group and associated invitations deleted successfully"}), 200
    except mysql.connector.Error as err:
        db.rollback()
        return jsonify({"error": str(err)}), 400


#previous code for creating group
# @app.route('/create_family_group', methods=['POST'])
# @token_required
# def create_family_group(user_id):
#     data = request.get_json()
#     group_name = data['group_name']
    
#     group_id = str(uuid.uuid4())
    
#     try:
#         cursor.execute("INSERT INTO family_groups (id, name) VALUES (%s, %s)", (group_id, group_name))
#         cursor.execute("UPDATE users SET group_id = %s WHERE id = %s", (group_id, user_id))
#         db.commit()
#         return jsonify({"message": "Family group created successfully!", "group_id": group_id}), 201
#     except mysql.connector.Error as err:
#         return jsonify({"error": str(err)}), 400

@app.route('/invite_family_member', methods=['POST'])
@token_required
def invite_family_member(user_id):
    data = request.get_json()
    receiver_phone = data['receiver_phone']
    group_id = data['group_id']
    
    try:
        cursor.execute("INSERT INTO invitations (sender_id, receiver_phone, group_id) VALUES (%s, %s, %s)", (user_id, receiver_phone, group_id))
        db.commit()
        return jsonify({"message": "Invitation sent successfully!"}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400

@app.route('/get_invitations', methods=['GET'])
@token_required
def get_invitations(user_id):
    cursor.execute("SELECT phone_number FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    phone_number = user['phone_number']
    
    cursor.execute("""
        SELECT i.id, i.sender_id, u.email AS sender_email, i.group_id, fg.name AS group_name
        FROM invitations i
        JOIN users u ON i.sender_id = u.id
        JOIN family_groups fg ON i.group_id = fg.id
        WHERE i.receiver_phone = %s AND i.status = 'pending'
    """, (phone_number,))
    
    invitations = cursor.fetchall()
    return jsonify(invitations), 200

@app.route('/respond_to_invitation', methods=['POST'])
@token_required
def respond_to_invitation(user_id):
    data = request.get_json()
    invitation_id = data['invitation_id']
    response = data['response']
    
    try:
        if response == 'accept':
            cursor.execute("SELECT group_id FROM invitations WHERE id = %s", (invitation_id,))
            group_id = cursor.fetchone()['group_id']
            cursor.execute("UPDATE users SET group_id = %s WHERE id = %s", (group_id, user_id))
            cursor.execute("UPDATE invitations SET status = 'accepted' WHERE id = %s", (invitation_id,))
        else:
            cursor.execute("UPDATE invitations SET status = 'declined' WHERE id = %s", (invitation_id,))
        db.commit()
        return jsonify({"message": f"Invitation {response}ed successfully!"}), 200
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400

@app.route('/add_medicine', methods=['POST'])
@token_required
def add_medicine(user_id):
    data = request.get_json()
    group_id = data['group_id']
    medicine_name = data['medicine_name']
    quantity = data['quantity']
    expiry_date = data['expiry_date']
    
    try:
        cursor.execute("""
            INSERT INTO inventory (group_id, medicine_name, quantity, expiry_date, added_by)
            VALUES (%s, %s, %s, %s, %s)
        """, (group_id, medicine_name, quantity, expiry_date, user_id))
        inventory_id = cursor.lastrowid
        
        cursor.execute("""
            INSERT INTO inventory_log (inventory_id, action, quantity, performed_by)
            VALUES (%s, 'added', %s, %s)
        """, (inventory_id, quantity, user_id))
        
        db.commit()
        return jsonify({"message": "Medicine added successfully!"}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400

@app.route('/get_inventory', methods=['GET'])
@token_required
def get_inventory(user_id):
    cursor.execute("SELECT group_id FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    group_id = user['group_id']
    
    cursor.execute("""
        SELECT i.*, u.email AS added_by_email
        FROM inventory i
        JOIN users u ON i.added_by = u.id
        WHERE i.group_id = %s
    """, (group_id,))
    
    inventory = cursor.fetchall()
    return jsonify(inventory), 200

@app.route('/get_inventory_log', methods=['GET'])
@token_required
def get_inventory_log(user_id):
    inventory_id = request.args.get('inventory_id')
    
    cursor.execute("""
        SELECT il.*, u.email AS performed_by_email
        FROM inventory_log il
        JOIN users u ON il.performed_by = u.id
        WHERE il.inventory_id = %s
        ORDER BY il.performed_at DESC
    """, (inventory_id,))
    
    log = cursor.fetchall()
    return jsonify(log), 200

@app.route('/get_user_group', methods=['GET'])
@token_required
def get_user_group(user_id):
    try:
        cursor.execute("""
            SELECT u.group_id, fg.name AS group_name
            FROM users u
            LEFT JOIN family_groups fg ON u.group_id = fg.id
            WHERE u.id = %s
        """, (user_id,))
        result = cursor.fetchone()
        if result and result['group_id']:
            return jsonify({"group_id": result['group_id'], "group_name": result['group_name']}), 200
        else:
            return jsonify({"message": "User is not in any group"}), 200
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400

#forgot password testing
def get_current_time():
    return datetime.now(pytz.UTC)

def send_email(to_email, subject, body):
    # Configure your email settings here
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = "your_email"
    smtp_password = "email_password"

    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)

@app.route('/forgot_password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data['email']

    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user:
        # Generate a unique token
        reset_token = secrets.token_urlsafe(32)
        expiration = get_current_time() + timedelta(hours=1)

        print(f"Generated token: {reset_token}")  # Debug print
        print(f"Expiration time: {expiration}")  # Debug print
        # Store the token in the database
        cursor.execute("UPDATE users SET reset_token = %s, reset_token_expires = %s WHERE id = %s",
                       (reset_token, expiration, user['id']))
        db.commit()

        # Send reset password email
        reset_link = f"http://localhost:5173/reset-password/{reset_token}"
        email_body = f"Click the following link to reset your password: {reset_link}"
        send_email(email, "Password Reset", email_body)

        return jsonify({"message": "Password reset link sent to your email"}), 200
    else:
        return jsonify({"error": "Email not found"}), 404

@app.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data['token']
    new_password = data['new_password']

    print(f"Received token: {token}")

    cursor.execute("SELECT id, reset_token_expires FROM users WHERE reset_token = %s", (token,))
    user = cursor.fetchone()

    if user:
        current_time = get_current_time()
        expiration_time = user['reset_token_expires']

        print(f"Current time: {current_time}")
        print(f"Token expiration: {expiration_time}")

        # Convert expiration_time to UTC
        if expiration_time.tzinfo is None:
            expiration_time = pytz.UTC.localize(expiration_time)

        if expiration_time > current_time:
            password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
            cursor.execute("UPDATE users SET password_hash = %s, reset_token = NULL, reset_token_expires = NULL WHERE id = %s",
                           (password_hash, user['id']))
            db.commit()
            return jsonify({"message": "Password reset successful"}), 200
        else:
            return jsonify({"error": "Token has expired"}), 400
    else:
        return jsonify({"error": "Invalid token"}), 400



if __name__ == '__main__':
    app.run(debug=True, port=5070)