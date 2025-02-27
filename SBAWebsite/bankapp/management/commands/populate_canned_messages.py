from django.core.management.base import BaseCommand
from bankapp.models import CannedMessage, CannedMessageCategory



class Command(BaseCommand):
    help = "Populates canned messages and categories for SecureBank"

    def handle(self, *args, **kwargs):
        # Define all categories and messages
        categories_and_messages = {
            "General Greetings": [
                {"title": "Welcome", "content": "Hello! Welcome to SecureBank. How can I assist you today?"},
                {"title": "General Assistance", "content": "Thank you for reaching out to SecureBank. How may I help you?"},
                {"title": "Loan Help", "content": "I'm here to help you with your loan application. How can I assist?"},
                {"title": "Business Support", "content": "Let me know how I can assist you with your business loan needs."},
                {"title": "General Welcome", "content": "Thank you for contacting SecureBank. How can we support your business today?"}
            ],
            "Loan Application Status": [
                {"title": "Under Review", "content": "Your loan application is currently under review. We will update you once a decision is made."},
                {"title": "Received", "content": "We have received your loan application. Our team is processing it."},
                {"title": "Pending", "content": "Your loan request is being evaluated. We appreciate your patience during this process."},
                {"title": "Final Review", "content": "Your application is in the final review stage. We will inform you of the decision shortly."},
                {"title": "Status Update", "content": "Your loan application status is pending. We will notify you of any updates."}
            ],
            "Loan Approval": [
                {"title": "Congratulations", "content": "Congratulations! Your loan application has been approved by SecureBank."},
                {"title": "Approval Notification", "content": "We are pleased to inform you that your loan has been approved. Details will follow shortly."},
                {"title": "Success", "content": "Your loan request has been successfully approved. Let's proceed with the next steps."},
                {"title": "Good News", "content": "SecureBank has approved your loan application. Our team will contact you soon."},
                {"title": "Approval Confirmation", "content": "Your business loan is approved. Please review the terms and conditions sent to your email."}
            ],
            "Loan Rejection": [
                {"title": "Declined", "content": "We regret to inform you that your loan application has been declined."},
                {"title": "Not Approved", "content": "After careful consideration, SecureBank is unable to approve your loan request at this time."},
                {"title": "Eligibility Issue", "content": "Your loan application has been declined due to eligibility criteria not being met."},
                {"title": "Unsuccessful", "content": "We are sorry to inform you that your loan request was not approved. For details, contact us."},
                {"title": "Reapply", "content": "Your application was declined. You may reapply once the necessary criteria are fulfilled."}
            ],
            "Request for Additional Information": [
                {"title": "More Documents Needed", "content": "We require additional documents to proceed with your loan application. Please provide them at your earliest convenience."},
                {"title": "Financial Statements Required", "content": "Could you please submit the necessary financial statements for further review?"},
                {"title": "Business Information", "content": "We need more information about your business to continue processing your loan request."},
                {"title": "Incomplete Application", "content": "Please provide the missing documentation to complete your loan application."},
                {"title": "Clarification Needed", "content": "To proceed, we need clarification on some details. Kindly check your email for more information."}
            ],
            "Follow-Up Messages": [
                {"title": "Follow-Up", "content": "We are following up on your loan application. Do you need any assistance?"},
                {"title": "Reminder", "content": "This is a reminder about the pending documents required for your loan application."},
                {"title": "Check-In", "content": "We wanted to check in and see if you need help completing your loan application."},
                {"title": "Document Submission", "content": "Following up on your document submission. Let us know if you need more time."},
                {"title": "Confirmation", "content": "Just a quick follow-up to ensure you received our previous message. Feel free to reach out with any questions."}
            ],
            "General Assistance": [
                {"title": "Loan Process Help", "content": "If you have any questions about the loan process, feel free to ask."},
                {"title": "Business Support", "content": "We are here to support your business financing needs. Let us know how we can assist."},
                {"title": "Loan Terms Help", "content": "Do you need help understanding the loan terms? We're here to help."},
                {"title": "Status Inquiry", "content": "For any inquiries about your loan status, contact us through this chat or email."},
                {"title": "Further Assistance", "content": "If you require further assistance, our team is available to help you."}
            ],

         "Waiting and Apologies": [
            {"title": "Patience Appreciation", "content": "Thank you for your patience. Your message is important to us. We'll be with you shortly."},
            {"title": "Representative Response", "content": "We appreciate your patience. One of our representatives will respond as soon as possible."},
            {"title": "Holding Confirmation", "content": "Thank you for holding. We are reviewing your request and will get back to you shortly."},
            {"title": "Wait Apology", "content": "We apologize for the wait. Our team is currently assisting other clients and will be with you soon."},
            {"title": "Processing Information", "content": "Thank you for waiting. We are processing your information and will provide an update shortly."},
            {"title": "High Demand Notice", "content": "We are currently experiencing high demand. We appreciate your patience and understanding."},
            {"title": "Delay Apology", "content": "We apologize for the delay. Your inquiry is important to us, and we are working to respond soon."},
            {"title": "Careful Handling", "content": "Thank you for your patience. Our team is handling your request with care and will reply shortly."},
            {"title": "Inconvenience Apology", "content": "We apologize for the inconvenience. We are working on your request and will update you soon."},
            {"title": "Commitment to Service", "content": "Thank you for waiting. We are committed to providing you with the best service possible."}
        ]

        }


        
        # Create categories and messages
        for category_name, messages in categories_and_messages.items():
            category, created = CannedMessageCategory.objects.get_or_create(name=category_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Category '{category_name}' created."))
            else:
                self.stdout.write(self.style.WARNING(f"Category '{category_name}' already exists."))
            
            for message in messages:
                CannedMessage.objects.get_or_create(
                    title=message["title"],
                    content=message["content"],
                    category=category,
                )
        
        self.stdout.write(self.style.SUCCESS("Canned messages and categories populated successfully."))
