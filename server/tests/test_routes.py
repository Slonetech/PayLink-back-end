
from api.models import User  # Import the necessary models




def test_routes(self):
    # Test with existing users
    response = app.test_client().get('/users')
    assert response.status_code == 200

