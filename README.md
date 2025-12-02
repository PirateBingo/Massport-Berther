During my time at MassPort, I became interested in the process of berthing cruise ships, and learned that it took a lot of time for the people to work out. From what I've learned, The process is simple enough to be automated by an AI. I'm working on a simple program to do this.

The left pane of my program is for editing the properties of ships according to their Side Shell Plan.

<img width="1890" height="491" alt="side_shell_plan" src="https://github.com/user-attachments/assets/7d813815-64fc-4b73-b59d-013bb6be41c5" />

Once the ship has valid properties, you can drag it into the ship map widget.

![1](https://github.com/user-attachments/assets/80f3266e-6795-437f-8fab-56f7b34b1f44)

Each ship can be converted into a .json file and shared with other users of the program. I will write the syntax for scene files, that will store ship schedule arrangements. Each ship can have a unique pattern and color.

The timeline explores the range in which the ship occupies the port

![2](https://github.com/user-attachments/assets/88b028ce-1e2a-4416-917f-0540ae493214)

Underneath the timeline is the scheduler. It's in the right pane normally, but like all widgets, it can be moved around and even displayed as its own window.

The scheduler selects the bollards for the cruise ships to berth to.

Taking an AI course my final semester of college, I learned about Constraint Satisfaction Problems. I now know that this AI problem is the ideal approach to finding the optimal ship schedule autonomously. A solution like this could easily be implemented with SciPy libraries in python.

I've worked on this project for about 18 hours in total now, and am very confident in my ability to see it through.
