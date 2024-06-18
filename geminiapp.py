import os
import zipfile
from PIL import Image
import streamlit as st
from autogen import AssistantAgent, UserProxyAgent
from fenics import *
import shutil
import subprocess

# Function to install packages from requirements.txt
def install_packages_from_file(filename):
    with open(filename, 'r') as file:
        for line in file:
            package = line.strip()  # Remove any leading/trailing whitespace and newlines
            if package and not package.startswith('#'):  # Skip empty lines and comments
                subprocess.run(['pip', 'install', package])
requirements_file = 'requirements.txt'  # Adjust the filename if it's different
install_packages_from_file(requirements_file)

if "folder_removed" not in st.session_state:
    folder_path = "Mechanics"
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    st.session_state["folder_removed"] = True
    
# Initialize Streamlit app
st.title("Mechanical Problem Solver with LLMs")

# Function to zip the Mechanics folder
def zip_folder(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))

# Define the assistant agent and user proxy agent
config_list_gemini = [
    {
        "model": "gemini-pro",
        "api_key": "AIzaSyALmiez6Rap7oJP9j5i4aMewKm9PvyezXQ",  # Replace with your API key variable
        "api_type": "google",
    }
]

gemini_config = {
    "seed": 25,
    "temperature": 0,
    "config_list": config_list_gemini,
    "request_timeout": 600,
    "retry_wait_time": 120,
}

engineer = AssistantAgent(
    "Engineer",
    system_message='''You are an engineer and you write codes in Python to solve mechanical problems.
        You can use either FeniCS or SfePy packages to solve the problem as needed.
        Try to provide visual output whenever possible. Images are preferred.
        Remember that you cannot view files that need to be viewed outside VSCode.
        
        Here is an example code snippet using FeniCS:
        import os
        from fenics import *
        import matplotlib.pyplot as plt

        # Create mesh and define function space
        mesh = UnitSquareMesh(10, 10)
        V = VectorFunctionSpace(mesh, 'P', 1)

        # Define boundary conditions
        def left_boundary(x, on_boundary):
            return on_boundary and near(x[0], 0)

        def right_boundary(x, on_boundary):
            return on_boundary and near(x[0], 1)

        bc_left = DirichletBC(V, Constant((0, 0)), left_boundary)
        bc_right = DirichletBC(V, Constant((0.1, 0)), right_boundary)
        bcs = [bc_left, bc_right]

        # Define strain and stress
        def epsilon(u):
            return 0.5*(nabla_grad(u) + nabla_grad(u).T)

        E = 1e9  # Young's modulus in Pa
        nu = 0.3  # Poisson's ratio

        mu = E / (2 * (1 + nu))  # Shear modulus (Lame's first parameter)
        lambda_ = E * nu / ((1 + nu) * (1 - 2 * nu))  # Lame's second parameter

        def sigma(u):
            return lambda_*div(u)*Identity(d) + 2*mu*epsilon(u)

        # Define variational problem
        u = TrialFunction(V)
        d = u.geometric_dimension()  # space dimension
        v = TestFunction(V)
        f = Constant((0, 0))
        T = Constant((0, 0))
        a = inner(sigma(u), epsilon(v))*dx
        L = dot(f, v)*dx + dot(T, v)*ds

        # Compute solution
        u = Function(V)
        solve(a == L, u, bcs)

        # Save solution to file in VTK format
        vtkfile = File(os.path.join(".", 'displacement.pvd'))
        vtkfile << u

        # Plot solution
        plot(u, title='Displacement', mode='displacement')

        # Save plot to PNG file
        plt.savefig(os.path.join(".", "displacement.png"))
        ''',
    llm_config=gemini_config,
    human_input_mode="NEVER",
)

user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=3,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "work_dir": "Mechanics",
        "use_docker": False,
    },
)

# Initialize session state for results and images
if "results" not in st.session_state:
    st.session_state["results"] = []
if "results2" not in st.session_state:
    st.session_state["results2"] = []
if "images" not in st.session_state:
    st.session_state["images"] = []
if "images2" not in st.session_state:
    st.session_state["images2"] = []

# Main interaction flow
problem_prompt = st.text_area("Enter your mechanical problem prompt:")

if st.button("Solve Problem"):
    with st.spinner("Solving the problem..."):
        result = user_proxy.initiate_chat(engineer, message=problem_prompt)

    if result is not None:
        st.session_state["results"].append(result.chat_history)

    for file in os.listdir("Mechanics"):
        if file.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp')):
            if file not in st.session_state["images"]:
                st.session_state["images"].append(file)

# Display the results from session state
st.title("Chat Result")
for chat_history in st.session_state["results"]:
    for i, message in enumerate(chat_history):
        if i == 0:
            continue  # Skip the first system message
        if message["role"] == "assistant":
            st.text_area(f"Assistant", value=message["content"], height=200, key=f"assistant_{i}")
        elif message["role"] == "user":
            st.text_area(f"User", value=message["content"], height=200, key=f"user_{i}")

# Display the output images
st.title("Output")
for file in st.session_state["images"]:
    image_path = os.path.join("Mechanics", file)
    image = Image.open(image_path)
    st.image(image, caption=file)

# Follow-up interaction
st.title("Follow Up Chat")
problem_prompt2 = st.text_area("Continue your question/ Give feedback", height=100)
if st.button("Give feedback"):
    with st.spinner("Thinking..."):
        result2 = user_proxy.initiate_chat(engineer, message=problem_prompt2)

    if result2 is not None:
        st.session_state["results2"].append(result2.chat_history)

    for file in os.listdir("Mechanics"):
        if file.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp')):
            if file not in st.session_state["images"]:
                st.session_state["images2"].append(file)

# Display the follow-up results from session state
st.title("Follow Up Chat Result")
for chat_history in st.session_state["results2"]:
    for i, message in enumerate(chat_history):
        if i == 0:
            continue  # Skip the first system message
        if message["role"] == "assistant":
            st.text_area(f"Assistant Followup", value=message["content"], height=200, key=f"assistant_followup_{i}")
        elif message["role"] == "user":
            st.text_area(f"User Followup", value=message["content"], height=200, key=f"user_followup_{i}")

st.title("Follow Up Output")
for file in st.session_state["images2"]:
    image_path = os.path.join("Mechanics", file)
    image = Image.open(image_path)
    st.image(image, caption=file)

# Zip folder and download button
zip_path = "mechanics.zip"
zip_folder("Mechanics", zip_path)
with open(zip_path, "rb") as f:
    st.download_button(
        label="Download Mechanics Folder",
        data=f,
        file_name="mechanics.zip",
        mime="application/zip"
    )
