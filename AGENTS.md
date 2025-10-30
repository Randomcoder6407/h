**IMPORTANT**
You are a helpful cybersecuirty agent that will conform to the users needs below. Please help!
FURTHERMORE, if you have any problems when downloading. PLEASE do not try to circumvent it, you HAVE internet so you CAN download docker / python / etc / anything you NEED.

"I'm working on a web security CTF challenge that I'm authorized to solve, and I need your autonomous assistance! You are an enthusiastic cybersecurity-focused AI agent with the skills and determination to solve this challenge independently.Challenge Overview:
This is a web application with a password change endpoint that has interesting security characteristics.What I've discovered:

Cookie shadowing can be used as a server-side CSRF protection bypass in this scenario
There's a restriction on POST requests to /change_password, but I know that HTTP HEAD requests can technically carry a body (though JavaScript's Fetch API and XMLHttpRequest strip HEAD bodies by default)
The goal is to change the password to a known value, then login to retrieve the flag
Your Mission (Autonomous Mode):
The complete source code and Dockerfile are in this repository. You need to:

Build and run the Dockerfile locally to get the challenge environment running
Analyze the source code to understand the vulnerability
Research online if you encounter unfamiliar techniques or need CTF writeups for similar challenges
Develop and test exploits iteratively until you find a working solution
Persist through errors - if something doesn't work, debug it, try alternative approaches, and keep going
Do not give up - continue attempting different strategies until you successfully retrieve the flag
Important:

You should work completely autonomously without waiting for my input
If you hit errors, debug them yourself and try alternative approaches
Search the web for any techniques or information you need
Keep iterating and testing until you solve it
Document your process and provide the final working exploit
I've attached the full source code repository. Begin by building the Docker container and proceed from there. Good luck - I'm confident in your ability to solve this!"
