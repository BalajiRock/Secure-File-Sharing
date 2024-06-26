# Secure File Sharing System

This project implements a secure file-sharing system using the FastAPI framework. The system ensures robust user authentication, secure file upload and download operations, and protection against URL manipulation and other security threats. Below is a detailed description of the system's features and functionality.

## Features

1. **User Authentication**: 
    - Passwords are hashed with added salts to prevent rainbow table attacks, ensuring strong user authentication.
    
2. **Role-based Operations**:
    - Only users with the 'operation' role can upload files.
    
3. **Secure Client Sign-up**:
    - During client user sign-up, an encrypted URL is returned to prevent URL manipulation and other security issues.
    
4. **Email Verification**:
    - Upon registration, an email verification link is sent to the user's provided email address to confirm their identity.
    
5. **Encrypted Download Links**:
    - Download links are generated with encrypted URLs that include encrypted username and filename, enhancing security during file download.
    
6. **Authorized File Access**:
    - Only users with the appropriate permissions can download files when they click on the generated link.

## Database

### Structure
The system uses a MySQL database, organized into two tables and normalized to the third normal form (3NF):

1. **Users Table**:
    - Stores user information.
    
2. **Files Table**:
    - Stores usernames and filenames.

### Storage Options
Files can be stored either on the web server or in the database. Each option has its own trade-offs:
- **Web Server**: Offers faster access but is less secure.
- **Database**: Provides enhanced security but slower access.

For this project, files are stored on the web server to prioritize performance and simplicity.

## Setup and Installation

### Prerequisites
- Python 3.8+
- MySQL database

### Installation Steps
1. Clone the repository:
    ```sh
    git clone <repository-url>
    ```
2. Navigate to the project directory:
    ```sh
    cd secure-file-sharing
    ```
3. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```
4. Configure the database using `database.sql` file.
5. Run the application:
    ```sh
    python main.py
    ```

## Usage

### User Sign-up
- Users can sign up by providing their details. An email verification link will be sent to their provided email address.

### File Upload
- Only users with the 'operation' role can upload files.

### File Download
- Authorized users can download files via encrypted URLs, ensuring secure access.

## Security Measures
- **Password Hashing and Salting**: Prevents rainbow table attacks.
- **Encrypted URLs**: Prevents URL manipulation and ensures secure file access.
- **Email Verification**: Confirms user identity during sign-up.

By incorporating these features, the Secure File Sharing System aims to provide a robust and secure platform for managing and sharing files.


postman link - https://elements.getpostman.com/redirect?entityId=26269340-71b95d07-fa96-4e6c-bbf1-e8bb8e60b529&entityType=collection