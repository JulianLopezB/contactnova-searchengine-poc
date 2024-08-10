# ContactNova Search Engine POC

This is a Proof of Concept (POC) for the ContactNova Search Engine, consisting of a FastAPI backend and a React frontend.

## Project Structure

- `backend/`: Contains the FastAPI backend application
- `frontend/`: Contains the React frontend application

## Prerequisites

- Python 3.11+
- Node.js 14+
- Docker and Docker Compose (optional, for containerized deployment)

## Quick Start

1. Clone the repository:
   ```
   git clone  https://gitlab.stefanini.com/ai/contactnova-poc.git
   cd contactnova-poc
   ```

2. Start the backend:
   - Follow the instructions in `backend/README.md`

3. Start the frontend:
   - Follow the instructions in `frontend/README.md`

4. Access the application at `http://localhost:3000`

## Docker Deployment

To deploy the entire application using Docker:

1. Ensure Docker and Docker Compose are installed on your system.

2. Build and start the containers:
   ```
   docker-compose up --build
   ```

3. Access the frontend at `http://localhost:3000` and the backend API at `http://localhost:8000`

## Development

For detailed instructions on developing each component, refer to the README files in the respective directories:

- Backend: `backend/README.md`
- Frontend: `frontend/README.md`

## License

This project is licensed under the MIT License.