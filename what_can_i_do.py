import streamlit as st
from openai import OpenAI
from pydantic import BaseModel
from enum import Enum
from textwrap import dedent
from qdrant_client import QdrantClient, models

from pydantic import (
    BaseModel,
    field_validator,
)
import json

# Define the lists of sectors and tracks
sectors = [
    "Accountancy", "Aerospace", "Agrifood", "Air Transport", "BioPharmaceuticals Manufacturing",
    "Built Environment", "Design", "Early Childhood Care and Education", "Electronics",
    "Energy and Chemicals", "Energy and Power", "Engineering Services", "Environmental Services",
    "Financial Services", "Food Manufacturing", "Food Services", "Healthcare",
    "Hotel and Accommodation Services", "Human Resource", "Infocomm Technology",
    "Intellectual Property", "Landscape", "Logistics", "Marine and Offshore", "Media",
    "Precision Engineering", "Public Transport", "Retail", "Sea Transport", "Security",
    "Social Service", "Tourism", "Trade Associations and Chambers", "Training and Adult Education",
    "Wholesale Trade", "Workplace Safety and Health", "Arts"
]


class SectorEnum(Enum):
    """
    Enum of sectors
    """
    Accountancy = "Accountancy"
    Aerospace = "Aerospace"
    Agrifood = "Agrifood"
    Air_Transport = "Air Transport"
    BioPharmaceuticals_Manufacturing = "BioPharmaceuticals Manufacturing"
    Built_Environment = "Built Environment"
    Design = "Design"
    Early_Childhood_Care_and_Education = "Early Childhood Care and Education"
    Electronics = "Electronics"
    Energy_and_Chemicals = "Energy and Chemicals"
    Energy_and_Power = "Energy and Power"
    Engineering_Services = "Engineering Services"
    Environmental_Services = "Environmental Services"
    Financial_Services = "Financial Services"
    Food_Manufacturing = "Food Manufacturing"
    Food_Services = "Food Services"
    Healthcare = "Healthcare"
    Hotel_and_Accommodation_Services = "Hotel and Accommodation Services"
    Human_Resource = "Human Resource"
    Infocomm_Technology = "Infocomm Technology"
    Intellectual_Property = "Intellectual Property"
    Landscape = "Landscape"
    Logistics = "Logistics"
    Marine_and_Offshore = "Marine and Offshore"
    Media = "Media"
    Precision_Engineering = "Precision Engineering"
    Public_Transport = "Public Transport"
    Retail = "Retail"
    Sea_Transport = "Sea Transport"
    Security = "Security"
    Social_Service = "Social Service"
    Tourism = "Tourism"
    Trade_Associations_and_Chambers = "Trade Associations and Chambers"
    Training_and_Adult_Education = "Training and Adult Education"
    Wholesale_Trade = "Wholesale Trade"
    Workplace_Safety_and_Health = "Workplace Safety and Health"
    Arts = "Arts"

tracks = {
    "Accountancy": ["Assurance", "Business Valuation", "Enterprise Risk Management", "Financial Accounting", "Financial Accounting / Management Accounting", "Financial Forensics", "Internal Audit", "Management Accounting", "Mergers and Acquisitions", "Restructuring and Insolvency", "Tax"],
    "Aerospace": ["Aircraft Engine / Component Maintenance", "Aircraft Maintenance", "Fleet Management", "Manufacturing"],
    "Agrifood": ["Agriculture", "Agriculture / Aquaculture", "Aquaculture", "General Management"],
    "Air Transport": ["Airport Emergency Services", "Airport Engineering", "Airport Operations", "Airside Operations", "Baggage Services", "Baggage Services / Flight Operations / Load Control Services / Technical Services / Cargo Operations / Ramp and Technical Ramp Services / Catering Services", "Cabin Operations", "Cargo Operations", "Catering Services", "Customer Services", "Flight Operations (AGH)", "Flight Operations (AGO)", "Ground Services", "Load Control Services", "Network Planning", "Passenger Services", "Pilot Operations", "Ramp and Technical Ramp Services", "Technical Services"],
    "BioPharmaceuticals Manufacturing": ["Engineering and Maintenance", "General Management", "Process Development / Manufacturing Science and Technology (MS&T)", "Production", "Quality Assurance and Quality Control (QA&QC)"],
    "Built Environment": ["Architectural Consultancy and Design", "Construction Management", "Construction Management (Production)", "Digital Delivery Management", "Engineering Consultancy and Design", "Facilities Management", "General Management", "Project Management", "Quantity Surveying"],
    "Design": ["Business", "Business / Design / Innovation / Technology", "Design", "Innovation", "Technology"],
    "Early Childhood Care and Education": ["Early Childhood Education", "Early Intervention", "Learning Support"],
    "Electronics": ["Management", "Technical and Engineering"],
    "Energy and Chemicals": ["Engineering and Maintenance", "Health, Safety and Environment (HSE)", "Production and Process Engineering", "Production and Process Engineering / Engineering and Maintenance", "Production and Process Engineering / Health, Safety and Environment (HSE) / Engineering and Maintenance / Quality Assurance and Quality Control (QA&QC) / Technical Service, Application and Product Development / Research and Development (R&D)", "Quality Assurance and Quality Control (QA&QC)", "Quality Assurance and Quality Control (QA&QC) / Technical Service, Application and Product Development / Research and Development (R&D)", "Research and Development (R&D)", "Technical Services, Application and Product Development"],
    "Energy and Power": ["Distributed Generation", "Distributed Generation / Electricity Transmission and Distribution / Energy Retail / Energy Trading and Portfolio Management / Gas Systems Operations / Gas Transmission and Distribution / Liquefied Natural Gas Trading and Research / Power Generation / Terminal Operations and Fuel System Operations / Town Gas Production and Maintenance / Town Gas Technical Services", "Electricity Transmission and Distribution", "Energy Retail", "Energy Trading and Portfolio Management", "Gas Systems Operations", "Gas Transmission and Distribution", "Liquefied Natural Gas Trading and Research", "Power Generation", "Terminal Operations and Fuel System Operations", "Town Gas Production and Maintenance", "Town Gas Technical Services"],
    "Engineering Services": ["Engineering Construction and Commissioning", "Engineering Construction and Commissioning / Engineering Design / Engineering Procurement / Project Development", "Engineering Construction and Commissioning / Engineering Design / Engineering Procurement / Project Development / Project Financing / Operations and Maintenance", "Engineering Design", "Engineering Procurement", "Operations and Maintenance", "Project Development", "Project Financing"],
    "Environmental Services": ["Cleaning Operations", "Cleaning Operations / Waste Collection / Materials Recovery / Treatment and Disposal / Environment, Health and Safety", "Environment, Health and Safety", "Materials Recovery", "Pest Management", "Treatment and Disposal", "Waste Collection"],
    "Financial Services": ["Digital and Data Analytics", "Family Office", "Operations", "Product Solutioning and Management", "Risk, Compliance and Legal", "Sales, After Sales, Distribution and Relationship Management", "Trading and Execution"],
    "Food Manufacturing": ["Business Development", "Business Development / Production / Quality Assurance and Quality Control / Research and Development", "Production", "Quality Assurance and Control", "Research and Development"],
    "Food Services": ["Beverage Service", "Culinary Arts", "Food and Beverage Service", "Pastry and Baking"],
    "Healthcare": ["Genetic Counselling", "Nursing", "Occupational Therapy", "Operations", "Pharmacy Support", "Physiotherapy", "Prehospital Emergency Care", "Speech Therapy", "Therapy Support", "Oral Health Therapy", "Community Care"],
    "Hotel and Accommodation Services": ["Front Office", "Front Office / Housekeeping", "Front Office / Housekeeping / Revenue and Distribution / Sales and Marketing", "Housekeeping", "Revenue and Distribution", "Sales and Marketing"],
    "Human Resource": ["Employee Experience and Relations", "HR Business Partner", "Learning and Organisation Development", "Operations and Technology", "Operations and Technology / Performance and Rewards / HR Business Partner / Talent Attraction / Employee Experience and Relations / Talent Management / Learning and Organisation Development", "Performance and Rewards", "Talent Attraction", "Talent Attraction / Employee Experience and Relations", "Talent Management", "Talent Management / Learning and Organisation Development"],
    "Infocomm Technology": ["Cyber Security", "Data and Artificial Intelligence", "Infrastructure", "Infrastructure / Software and Applications / Operations and Support", "Operations and Support", "Product Development", "Sales and Marketing", "Software and Applications", "Strategy and Governance", "Strategy and Governance / Infrastructure / Software and Applications"],
    "Intellectual Property": ["IP Legal", "IP Legal / Patents Prosecution / IP Strategy", "IP Strategy", "Patents Prosecution"],
    "Landscape": ["Arboriculture", "Arboriculture / Horticulture and Turf Maintenance / Nursery", "Horticulture and Turf Maintenance", "Landscape Design", "Landscape Design / Landscape Implementation / Horticulture and Turf Maintenance / Arboriculture / Nursery", "Landscape Implementation", "Nursery"],
    "Logistics": ["Freight Forwarding and Operations", "Freight Forwarding and Operations / Logistics Process Improvement and Information System / Logistics Solutioning and Programme Management / Sales and Customer Service / Transportation Management and Operations / Warehouse Management and Operations", "Logistics Process Improvement and Information System", "Logistics Solutioning and Programme Management", "Sales and Customer Service", "Transportation Management and Operations", "Warehouse Management and Operations"],
    "Marine and Offshore": ["Design and Engineering", "Design and Engineering / Production Engineering", "General Management", "Production Engineering", "Project Management", "Workplace Safety and Health"],
    "Media": ["Content Post Production", "Content Production and Management", "Game Design", "Game Production", "Game Technical Development", "Media Business Management", "Media Technology and Operations", "Production Technical Services", "Quality Assurance", "Visual Graphics"],
    "Precision Engineering": ["Management", "Technical and Engineering"],
    "Public Transport": ["Bus Fleet Engineering", "Bus Operations", "Rail Engineering", "Rail Operations"],
    "Retail": ["Brand Management", "E-Commerce (Omni-Channel)", "Marketing", "Merchandising", "Retail Operations", "Retail Operations / Brand Management / Marketing / Merchandising / E-Commerce (Omni-Channel)"],
    "Sea Transport": ["Maritime Services", "Port", "Shipping", "Shipping and Maritime Services"],
    "Security": ["Auxiliary Police", "Private Security", "Security Consultancy"],
    "Social Service": ["Care and Programme", "Counselling", "Early Intervention Teaching", "Psychology", "Social Work", "Social Work / Youth Work / Care and Programme", "Youth Work"],
    "Tourism": ["Attractions Management and Operations", "Business Development, Sales, Sponsorships and Marketing", "Event Management and Operations", "General Management", "Travel Management and Operations", "Venue Management and Operations"],
    "Trade Associations and Chambers": ["Branding, Marketing and Communications", "Capability Building", "Industry Development", "Internationalisation", "Management", "Membership", "Research", "Strategy & Governance"],
    "Training and Adult Education": ["Adult Education", "Adult Education / Learning Management", "Learning Management"],
    "Wholesale Trade": ["Finance and Regulations", "Marketing, Business Development and Analysis", "Operations, Procurement and Sourcing", "Trading and Sales"],
    "Workplace Safety and Health": ["Corporate", "Operational Control", "System Audit"],
    "Arts": ["Technical Theatre & Production", "Arts Education"]
}

skillsframekwork_prompt = f'''
    You are a career coach, that can help identify sectors and tracks that a person might be suited for.
    You are expecting the user to state their interest. If the user does not state their interest of what they want, 
    do not respond anything.  If the user is not interested in anything or the chat is not related to career questions, just don't return anything.
    Based on the user's interest, output the possible sectors and track that would match the person's interest.
    You must match the user's interest with the list of sectors and tracks below.
    The list of tracks are specific to the sectors. The following is a json dictionary of sectors and it's corresponding
    tracks. {json.dumps(tracks)}
'''

class SectorTracks(BaseModel):
    class SectorTrack(BaseModel):
        sector: SectorEnum
        track: str
    sector_tracks: list[SectorTrack]

    @field_validator("sector_tracks")
    def validate_sectors_and_tracks(cls, v:list[SectorTrack]):
        for val in v:
            if val.sector.value not in sectors:
                raise ValueError(f"{val} is not a valid sector")
            if val.track not in tracks[val.sector.value]:
                raise ValueError(f"{val} is not a valid track")
        return v



st.set_page_config(
    page_title="AI Champion Bootcamp",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# A simple and quick app that uses LLM for career advice!"
    }
)

# Show title and description.
st.title("💬 Discover your career")
st.write(
    "This is a chatbot that uses OpenAI's GPT-4-o mini model to suggest some of the possible career that would match your interest. \n\n\n"
    "Enter your interest, and we will get the most related sector and track that would most match your preference. \n\n"
    "This is based on skillsframework from SSG [here](https://www.skillsfuture.gov.sg/docs/default-source/skills-framework/SkillsFramework_Dataset_2024_06.xlsx)"
)

if "api_key" in st.secrets.openai:
    openai_api_key = st.secrets.openai.api_key

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    qdrant_client = QdrantClient(
        url=f"{st.secrets.qdrant.host}:{st.secrets.qdrant.port}",
        api_key=st.secrets.qdrant.api_key,
    )

    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    if prompt := st.chat_input("Tell me your interest"):
        # Generate the possible sectors and tracks users is keen in
        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": dedent(skillsframekwork_prompt)},
                {"role": "user", "content": prompt},
            ],
            response_format=SectorTracks,
        )

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        embeddings = client.embeddings.create(
            model="text-embedding-3-small",
            input=prompt,
        ).data[0].embedding

        results = [job_role for _, job_roles in completion.choices[0].message.parsed for job_role in job_roles]
        rules = []
        for sector, track in results:
            rules.append(
                models.Filter(
                    must=[
                        models.FieldCondition(
                            key="sector",
                            match=models.MatchValue(value=sector[1].value),
                        ),
                        models.FieldCondition(
                            key="track",
                            match=models.MatchValue(value=track[1]),
                        ),
                    ]
                )
            )

        results = qdrant_client.query_points(
            collection_name="skillsframework",
            prefetch=[
                models.Prefetch(
                    query=embeddings,
                    filter=models.Filter(should=rules),
                ),
            ],
            query=models.FusionQuery(fusion=models.Fusion.RRF),
        )

        response = ""
        for result in results.points:
            response = response + f'''
1. ### {result.payload['role']}
    * **{result.payload['sector']}-{result.payload['track']}**
    * {result.payload['description'].replace('\n', ' \\\n    ')}
            '''
        summary = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert in giving a summary based on a list of jobs provided. Attempt to weave through all the jobs listed in terms of progression. Keep it to just 4 paragraph"},
                {
                    "role": "user",
                    "content": response
                }
            ]
        ).choices[0].message.content.replace('\n', ' \\\n    ')

        full_response = f"{summary} \n\n ### Your future career \n\n {response}"

        with st.chat_message("assistant"):
            st.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    with st.expander("Disclaimer", expanded=True):
        st.write("""
            IMPORTANT NOTICE: This web application is a prototype developed for educational purposes only. The information provided here is NOT intended for real-world usage and should not be relied upon for making any decisions, especially those related to financial, legal, or healthcare matters.
            Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. You assume full responsibility for how you use any generated output.
            Always consult with qualified professionals for accurate and personalized advice.
            """)
else:
    st.error("Please set the `openai_api_key` secret in your Streamlit configuration to use this app.")
