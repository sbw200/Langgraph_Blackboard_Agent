# README.md

## Installation

1. Clone the repository:
```
git clone https://github.com/your-username/your-project.git
```
2. Install the required dependencies:
```
pip install -r requirements.txt
```

## Usage

1. Set the environment variables:
```
export NAME=your_username
export PASSWORD=your_password
export QDRANT_KEY=your_qdrant_key
export QDRANT_url=your_qdrant_url
TAVILY_API_KEY=
MISTRAL_API_KEY=
LANGSMITH_API_KEY=
```
2. Run the main script:

You will need at least two (or three, if using ngrok) separate terminal windows for this.

Start the FastAPI Backend:

Open a new terminal window.

Navigate to the backend directory:


```
cd C:\...\BlackboardProject\backend
```
Activate your Python virtual environment (if you created one):

Run the FastAPI application using Uvicorn:

```
uvicorn main:app --reload --port 8000
```

Keep this terminal open. You should see Uvicorn running on http://127.0.0.1:8000.

(Optional) Expose Backend with ngrok (for Public Access):
If you want your chatbot to be accessible from other devices or over the internet:

Ensure ngrok is installed and authenticated on your system (refer to ngrok's official documentation for setup).

Open a separate, new terminal window.

Run ngrok, providing the full path to ngrok.exe if it's not in your system's PATH:

```
"C:\Users\...\ngrok.exe" http 8000
```

Look for the Forwarding line in the ngrok output. It will provide an https:// URL (e.g., https://abcdef12345.ngrok-free.app). Copy this URL.

Keep this terminal open.

Update frontend/.env.local:
Go back to your frontend/.env.local file and replace http://localhost:8000 with the copied ngrok https:// URL. Save the file.

Start the Next.js Frontend:

Open a third terminal window.

Navigate to the frontend directory:

cd C:\.....\BlackboardProject\frontend

Start the Next.js development server:

```
npm run dev
```

The terminal will show the local URL (e.g., http://localhost:3000 or http://localhost:3001).

Access the Chatbot
Open your web browser and go to the URL provided by the npm run dev command (e.g., http://localhost:3001).```

## API

The project provides the following API endpoints:

- `GET /`: Returns a message indicating that the LangGraph chatbot is live.
- `POST /chat`: Handles chat requests and returns the chatbot's response.

## Contributing

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your-feature`.
3. Make your changes and commit them: `git commit -am 'Add some feature'`.
4. Push to the branch: `git push origin feature/your-feature`.
5. Submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Testing

To run the tests, execute the following command:
```
python test.py
```
