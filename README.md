# Flights Chatbot Assistant

**Objective**: Have a chatbot assistant for customers of an airline that can respond to their inquiries and questions about their flights, seat upgrades, miles redemption and check-in process

## User stories:

| # | User Story | Acceptance Criteria | REST Endpoint |
|---|------------|---------------------|----------------|
| 1 | **User Registration** <br> As a new user, I want to register an account so that I can access and manage my flight bookings. | - Form includes: name, email, password (and optional phone)<br>- Email must be unique and valid<br>- Password meets security rules<br>- Confirmation message/email sent<br>- User is redirected to login or auto-logged in | POST /users/register |
| 2 | **User Login** <br> As a registered user, I want to log in to my account so that I can securely access my personal flight information. | - Form includes email and password<br>- Valid credentials log in the user<br>- Invalid credentials show error<br>- Password reset available<br>- Session maintained securely | POST /users/login |
| 3 | **Book Flights** <br> As a logged-in user, I want to search for and book flights so I can plan my travel. | - User can search by origin, destination, date<br>- Flights with details are shown<br>- User can select and book a flight<br>- Success message on booking<br>- Flight appears in upcoming list | GET /flights/search<br>POST /bookings |
| 4 | **View My Flights** <br> As a logged-in user, I want to see upcoming and past flights so I can manage my trips. | - Flights grouped as upcoming and past<br>- Each flight shows details (date, airline, status)<br>- Only user’s flights are shown<br>- Sorted by date | GET /users/{userId}/bookings<br>(Optional: ?status=upcoming) |
| 5 | **Cancel a Flight** <br> As a logged-in user, I want to cancel a booked flight if plans change. | - Only upcoming flights can be cancelled<br>- Confirmation prompt required<br>- Success message after cancel<br>- Flight marked as cancelled or removed from upcoming list<br>- Cancellation rules enforced | DELETE /bookings/{bookingId}<br>PATCH /bookings/{bookingId}<br>{ "status": "cancelled" } |
| 6 | **Chatbot for FAQs** <br> As a logged-in user, I want to use a chatbot to get answers to common questions quickly. | - Chatbot accessible from main UI<br>- Responds to common questions<br>- Offers help or redirection when needed<br>- Session preserved for chat<br>- Chat does not require repeated login | POST /chatbot/message<br>{ "message": "Your question here" } |
