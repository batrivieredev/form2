from backend.app import create_app
from dotenv import load_dotenv
import os

load_dotenv()

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    # Debug activé pour afficher les erreurs détaillées
    app.run(host='0.0.0.0', port=port, debug=True)
