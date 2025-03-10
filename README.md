# CS122A Project

## Setup Instructions

1. Clone the repository:
    ```sh
    git clone https://github.com/con169/cs122a-project.git
    cd cs122a-project
    ```
2. Create and activate virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate  # macOS/Linux
    venv\Scripts\activate     # Windows
    ```

3. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up environment variables by creating a `.env` file with:
    ```sh
    DB_HOST=your_host
    DB_USER=your_user
    DB_PASSWORD=your_password
    DB_NAME=your_database
    ```

5. Run using command line:
``` python project.py ```