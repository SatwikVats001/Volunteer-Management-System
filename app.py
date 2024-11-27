import os
from flask import Flask, render_template, request, redirect, url_for, flash, session,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from pymongo.server_api import ServerApi

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # For flash messages and session management
app.permanent_session_lifetime = timedelta(minutes=30)  # Set session timeout to 30 minutes
 
"""Data Base Connection to a Cloud"""
# Connect to MongoDB
client = MongoClient('mongodb+srv://mayanksharma12662:root@mayank.chjb6.mongodb.net/?retryWrites=true&w=majority&appName=Mayank')
db = client['event_management']  # Database name
users_collection = db['users']  # Users collection
events_collection = db['events']  # Events collection
notifications_collection = db['notifications']  # Notifications collection
approved_volunteers_collection = db['approved_volunteers']  # Approved volunteers collection
employees_collection = db['employees']





CHATBOT_RESPONSES = {
    "greet": "Hello! How can I assist you today?",
    "volunteer": "You can sign up to be a volunteer by visiting our registration page.",
    "hours": "Our volunteers work from 9 AM to 5 PM.",
    "location": "We are located at 123 Volunteer St.",
    "how to become a volunteer": "You can become a volunteer by filling out the registration form on our website.",
    "who can volunteer": "Anyone aged 18 or older can volunteer. There are also opportunities for younger volunteers with parental consent.",
    "what is the minimum age to volunteer": "The minimum age to volunteer is 18. However, younger individuals can volunteer with parental consent.",
    "do I need any experience to volunteer": "No experience is required. We provide all the necessary training.",
    "what kind of tasks do volunteers do": "Volunteers help with a variety of tasks including event coordination, outreach, administration, and community support.",
    "is there a volunteer training": "Yes, we offer a volunteer orientation and training program. It will help you get familiar with our processes.",
    "how do I register as a volunteer": "You can register as a volunteer by filling out the registration form on our website or by contacting our volunteer coordinator.",
    "can I volunteer remotely": "Yes, there are remote volunteer opportunities depending on the project. Check our website for more information.",
    "how many hours do I need to volunteer": "We recommend a minimum of 5 hours per week, but the number of hours depends on your availability and the projects you choose.",
    "can I choose my volunteer shifts": "Yes, you can choose from available shifts based on your schedule.",
    "what are the shifts for volunteering": "We offer morning shifts (9 AM to 12 PM), afternoon shifts (12 PM to 3 PM), and evening shifts (3 PM to 6 PM).",
    "how can I change my shift": "You can change your shift by logging into your account on our website and updating your availability.",
    "what happens if I miss my shift": "If you miss a shift, please notify us as soon as possible. We understand that things happen, but consistent attendance is important.",
    "do volunteers get paid": "Volunteers do not receive payment. However, we do offer certificates of appreciation and other incentives.",
    "can I get a certificate for volunteering": "Yes, you can receive a certificate for your volunteer hours upon completion of your service.",
    "can I volunteer as a group": "Yes, we welcome group volunteers. Please contact us in advance to arrange group opportunities.",
    "what are the benefits of volunteering": "Volunteering provides an opportunity to make a difference in your community, gain experience, and meet like-minded individuals.",
    "how can I contact the volunteer coordinator": "You can contact the volunteer coordinator via email at volunteer@ourorganization.com or by calling 123-456-7890.",
    "can I volunteer if I am under 18": "Yes, if you're under 18, you can still volunteer with parental consent. Please contact us for further information.",
    "how do I log my volunteer hours": "You can log your volunteer hours through your profile page on our website after each shift.",
    "how do I cancel my volunteer registration": "If you'd like to cancel your volunteer registration, please contact us via email or phone.",
    "can I get feedback for my volunteering experience": "Yes, we provide feedback at the end of each volunteer project to help you grow and improve.",
    "how do I find upcoming volunteer opportunities": "You can find upcoming opportunities by checking the volunteer section of our website or by signing up for our newsletter.",
    "is there a minimum commitment to volunteer": "There is no minimum commitment. However, regular volunteering is appreciated for continuity and effectiveness in our projects.",
    "how do I register for a specific event": "To register for a specific event, please visit our event page on the website and select the volunteer registration link.",
    "what should I bring for my shift": "You should bring a positive attitude, comfortable clothing, and any necessary materials as specified by your event coordinator.",
    "what is the dress code for volunteers": "Volunteers are encouraged to wear comfortable clothing and closed-toe shoes. Specific events may have different dress codes, so please check in advance.",
    "do you provide transportation for volunteers": "We do not provide transportation, but we offer suggestions for public transport routes to the event location.",
    "can I volunteer if I have a disability": "Yes, we are committed to providing inclusive volunteer opportunities for individuals with disabilities. Please contact us to discuss specific needs.",
    "how do I track my volunteer hours": "You can track your volunteer hours directly on your profile page on our website. It will update after each shift is completed.",
    "what is the volunteer recognition program": "Our volunteer recognition program includes awards, certificates, and thank-you events for those who have made significant contributions.",
    "how do I refer a friend to volunteer": "You can refer a friend by sending them the volunteer registration link from our website or by providing their contact details to us.",
    "do you have any summer volunteer programs": "Yes, we have several summer volunteer programs. Please check our website for available opportunities.",
    "can I volunteer if I don't live locally": "Yes, we accept volunteers from outside the local area. Remote opportunities are also available.",
    "how can I become a team leader for a project": "To become a team leader, you need to have significant experience and demonstrate leadership skills. Contact us for more information about the application process.",
    "can I get a recommendation letter for my volunteer work": "Yes, we provide recommendation letters for volunteers who have made a consistent and significant contribution.",
    "are there any volunteer events this week": "Please check our events calendar on the website for upcoming volunteer events this week.",
    "how can I stay updated with volunteer opportunities": "You can stay updated by subscribing to our newsletter, following us on social media, or regularly checking the volunteer section on our website.",
    
}


@app.route('/')
def index():
    return render_template('home.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form['message']
    
    # Check if the message matches any of the predefined questions
    response = CHATBOT_RESPONSES.get(user_message.lower(), "Sorry, I didn't understand that.")
    
    return jsonify({"response": response})


#########################################################################################################################################
#----------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------
#########################################################################################################################################
"""This is a route for homescreen or itroduction page of our site. i.e. home.html"""


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('Policy.html')

#########################################################################################################################################
#----------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------
#########################################################################################################################################
"""Signup Page for a new user/employee registration"""

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role = request.form['role']  # Either 'admin' or 'employee'

        # Check if username already exists in MongoDB
        if users_collection.find_one({'username': username}):
            flash('Username already exists!', 'danger')
        else:
            hashed_password = generate_password_hash(password)
            users_collection.insert_one({
                'username': username,
                'password': hashed_password,
                'email': email,
                'role': role
            })
            flash('Sign up successful! You can now log in.', 'success')
            return redirect(url_for('login'))

    return render_template('signup.html')

#########################################################################################################################################
#----------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------
#########################################################################################################################################
"""Login Page for a login od a site."""

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Fetch user from MongoDB
        user = users_collection.find_one({'username': username})

        if not user:
            flash('Username does not exist!', 'danger')
        else:
            if check_password_hash(user['password'], password):
                session['username'] = username
                session['role'] = user['role'].lower()

                # Redirect to the respective dashboard
                if session['role'] == 'admin':
                    return redirect(url_for('admin_dashboard'))
                elif session['role'] == 'employee':
                    return redirect(url_for('employee_dashboard'))
            else:
                flash('Incorrect password!', 'danger')

    return render_template('login.html')

#########################################################################################################################################
#----------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------
#########################################################################################################################################
"""Admin Section"""

@app.route('/admin-dashboard')
def admin_dashboard():
    if 'username' not in session or session.get('role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))

    return render_template('admin_dashboard.html')

#----------------------------------------------------------------------------------------------------------------------------------------
@app.route('/add-event', methods=['GET', 'POST'])
def addEvent():
    if 'username' not in session or session.get('role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Retrieve form data
        event_name = request.form.get('event_name')
        event_description = request.form.get('event_description')
        contact_details = request.form.get('contact')
        event_date = request.form.get('event_date')
        event_time = request.form.get('event_time')
        event_location = request.form.get('event_location')
        

        # Validate required fields
        if not event_name or not event_description or not event_date or not event_time or not event_location:
            flash('All fields are required!', 'danger')
            return render_template('addEvent.html')

        # Combine event date and time
        event_datetime = datetime.strptime(f'{event_date} {event_time}', '%Y-%m-%d %H:%M')

        # Save the event to MongoDB
        try:
            event = {
                'name': event_name,
                'description': event_description,
                'datetime': event_datetime,  # Save as a single datetime field
                'location': event_location,
                'created_by': session['username'],  # Log the admin who created it
                'created_at': datetime.now()  # Add a timestamp
            }
            events_collection.insert_one(event)  # Save to events collection
            flash('Event added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            flash(f'An error occurred while adding the event: {e}', 'danger')

    # Render the Add Event page for GET requests
    return render_template('addEvent.html')


#----------------------------------------------------------------------------------------------------------------------------------------

@app.route('/manage-interests')
def manage_interests():
    if 'username' not in session or session.get('role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))

    notifications = list(notifications_collection.find({'to_role': 'admin'}))
    return render_template('manage_interests.html', notifications=notifications)

@app.route('/respond-interest/<notification_id>/<action>', methods=['POST'])
def respond_interest(notification_id, action):
    if 'username' not in session or session.get('role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))

    notification = notifications_collection.find_one({'_id': ObjectId(notification_id)})
    if not notification:
        flash('Notification not found!', 'danger')
        return redirect(url_for('manage_interests'))

    event_name = notification['message'].split(':')[-1].strip()
    event = events_collection.find_one({'name': event_name})
    if not event:
        flash('Associated event not found!', 'danger')
        return redirect(url_for('manage_interests'))

    employee_username = notification['from']

    if action == 'approve':
        events_collection.update_one(
            {'_id': event['_id']},
            {'$addToSet': {'volunteers': employee_username}}
        )
        store_approved_volunteer(employee_username, event)
        flash(f'{employee_username} has been assigned to the event!', 'success')

    employee_notification = {
        'message': f"Your interest in the event '{event_name}' has been {'approved' if action == 'approve' else 'rejected'}.",
        'from': session['username'],
        'timestamp': datetime.now(),
        'to_user': employee_username
    }
    notifications_collection.insert_one(employee_notification)
    notifications_collection.delete_one({'_id': ObjectId(notification_id)})

    return redirect(url_for('manage_interests'))

def store_approved_volunteer(username, event):
    approved_volunteer = {
        'username': username,
        'event_name': event['name'],
        'event_id': event['_id'],
        'approved_at': datetime.now()
    }
    approved_volunteers_collection.insert_one(approved_volunteer)

@app.route('/approved-volunteers', methods=['GET'])
def get_approved_volunteers():
    try:
        volunteers = list(approved_volunteers_collection.find())
        for volunteer in volunteers:
            volunteer['_id'] = str(volunteer['_id'])

        return render_template('approved_volunteers.html', volunteers=volunteers)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

#########################################################################################################################################
#----------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------
#########################################################################################################################################

"""<---Employee Section--->"""

@app.route('/employee-dashboard')
def employee_dashboard():
    username = session.get('username')

    if not username:
        return redirect(url_for('login'))

    # Fetch total number of events
    total_events = events_collection.count_documents({})

    # Fetch total tasks assigned to the logged-in user
    tasks_assigned = approved_volunteers_collection.count_documents({"username": username})

    # Fetch pending tasks for the user
    pending_tasks = total_events - tasks_assigned

    return render_template(
        'employee_dashboard.html',
        username=username,
        total_events=total_events,
        tasks_assigned=tasks_assigned,
        pending_tasks=pending_tasks
    )

@app.route('/chart-data')
def chart_data():
    username = session.get('username')
    if not username:
        return jsonify({"error": "Unauthorized"}), 401

    total_events = events_collection.count_documents({})
    tasks_assigned = approved_volunteers_collection.count_documents({"username": username})
    pending_tasks = total_events - tasks_assigned

    # Chart data
    chart_data = {
        "labels": ["Total Events", "Tasks Assigned", "Pending Tasks"],
        "values": [total_events, tasks_assigned, pending_tasks]
    }
    return jsonify(chart_data)

#----------------------------------------------------------------------------------------------------------------------------------------

@app.route('/show-event')
def show_event():

    if 'username' not in session or session.get('role') != 'employee':
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))

    events = list(events_collection.find())  # Fetch all events
    return render_template('show_event.html', events=events)
#----------------------------------------------------------------------------------------------------------------------------------------

@app.route('/interested/<event_id>', methods=['POST'])
def interested_in_event(event_id):
    if 'username' not in session or session.get('role') != 'employee':
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))

    event = events_collection.find_one({'_id': ObjectId(event_id)})
    if not event:
        flash('Event not found!', 'danger')
        return redirect(url_for('show_event'))

    # Add a notification for the admin
    notification = {
        'message': f"{session['username']} is interested in the event: {event['name']}",
        'from': session['username'],
        'timestamp': datetime.now(),
        'to_role': 'admin'
    }
    db['notifications'].insert_one(notification)

    flash('Your interest has been sent to the admin!', 'success')
    return redirect(url_for('show_event'))
#----------------------------------------------------------------------------------------------------------------------------------------


@app.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    if 'username' not in session:
        flash('Please log in first!', 'danger')
        return redirect(url_for('login'))
    
    # Fetch user data from MongoDB
    user = users_collection.find_one({'username': session['username']})
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        profile_picture = request.files['profile_picture']
        
        # Update profile picture if present
        if profile_picture:
            filename = secure_filename(profile_picture.filename)
            profile_picture.save(os.path.join('static/uploads', filename))  # Save the image

        # Update user data in the database
        users_collection.update_one(
            {'username': session['username']},
            {'$set': {'name': name, 'email': email, 'profile_picture': filename if profile_picture else user.get('profile_picture')}}
        )

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('employee_dashboard'))  # Redirect to the dashboard after update
    
    return render_template('edit_profile.html', user=user)
#----------------------------------------------------------------------------------------------------------------------------------------



##########################################################################################################################################
#-----------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------
#########################################################################################################################################
"""<---Notification Section--->"""

@app.route('/notifications')
def notifications():
    if 'username' not in session:
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))

    # Fetch notifications specific to the logged-in user
    notifications = list(db['notifications'].find({'to_user': session['username']}))
    return render_template('notification.html', notifications=notifications)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))



@app.route('/assign_tasks/<username>')
def assign_tasks(username):
    # Fetch user from users collection
    user = users_collection.find_one({"username": username})
    
    if user:
        # Fetch approved events for this user
        tasks = approved_volunteers_collection.find({"username": username})
        
        # Fetch event details to get the 'created_by' field
        enriched_tasks = []
        for task in tasks:
            event = events_collection.find_one({"name": task['event_name']})
            if event:
                task['created_by'] = event['created_by']  # Add the creator's name
            else:
                task['created_by'] = "Unknown"
            enriched_tasks.append(task)
        
        return render_template('tasks.html', tasks=enriched_tasks, username=username)
    else:
        return f"No user found with username {username}", 404








if __name__ == '__main__':
    app.run(debug=True)
