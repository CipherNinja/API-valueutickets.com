from django.contrib import messages

class MailErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Fetch email_message from the instance or context
        email_message = getattr(request, 'email_message', None)  # Replace with actual retrieval logic
        if email_message:
            if "Success" in email_message:
                messages.success(request, email_message)
            elif "Failure" in email_message:
                messages.error(request, email_message)

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Optional: Inject logic to ensure email_message is accessible in the request object
        pass



