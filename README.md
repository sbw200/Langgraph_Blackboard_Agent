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
```
python main.py
```

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
