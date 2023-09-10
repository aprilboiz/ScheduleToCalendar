# ScheduleToCalendar

Automatically convert your school's hard-to-read schedule from the website into your Google Calendar.

## Table of Contents

- [ScheduleToCalendar](#scheduletocalendar)
  - [Table of Contents](#table-of-contents)
  - [Project Description](#project-description)
  - [Installation](#installation)
    - [Prerequisites](#prerequisites)
    - [Installation Steps](#installation-steps)
  - [Usage](#usage)
    - [Windows](#windows)
  - [License](#license)
  - [Disclaimer](#disclaimer)
  - [Acknowledgments](#acknowledgments)

## Project Description

Do you find your school's website schedule a headache to read? This project aims to simplify your life by converting your school schedule into Google Calendar events.

**Note:**
- This project is a work in progress.
- Google Calendar API credentials and configurations are not included in this script.

<!-- By now, `ScheduleToCalendar` supports below schools:
- SGU ([Saigon University](https://www.sgu.edu.vn/))
- HUFLIT ([HCMC University of Foreign Languages - Information Technology](https://huflit.edu.vn/)) -->

## Installation

### Prerequisites
- [Python](https://www.python.org/) >= 3.10
- Required packages listed in `requirements.txt`.
- The `credentials.json` file in the `api` folder.

### Installation Steps
1. Clone this repository.
   ```bash
   git clone https://github.com/tuananhphann/ScheduleToCalendar.git
   cd ScheduleToCalendar
   ```

2. Install the required packages.
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Windows
In the project directory, run this command
```powershell
python .\main.py
```
Then follow the prompts.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

**IMPORTANT:** This project involves handling user credentials, including usernames and passwords. Please read this disclaimer carefully before using or contributing to this project.

1. **User Responsibility**: You are responsible for managing your own credentials, including usernames and passwords.

2. **Secure Storage**: While this project prioritizes security, no system is entirely immune to risks. We do not store user passwords in any form.

3. **No Sharing**: Never share your username or password with anyone, including project maintainers or contributors. Project maintainers and contributors will never request your password.

4. **Third-Party Services**: This project may interact with third-party services or APIs that require authentication. Review and comply with the terms and privacy policies of these services.

5. **Liability**: Project maintainers and contributors are not liable for unauthorized access, data breaches, or other security incidents related to user credentials. Using this project implies acknowledgment and acceptance of the associated credential management risks.

6. **Legal Compliance**: Ensure your use of this project complies with all applicable laws and regulations regarding user credential handling, including data protection and privacy laws.

By using or contributing to this project, you agree to the terms and conditions outlined in this disclaimer. If you do not agree with these terms, please refrain from using or contributing to this project.

## Acknowledgments
Thanks to ChatGPT helped me create the README.md file.
