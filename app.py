from models.database import Database
from models.nl2query import NL2Query
from models.llm_helpers import GenerateByLLM
from dotenv import load_dotenv
import warnings
warnings.filterwarnings('ignore')

load_dotenv()
db = Database()
llm_generator = GenerateByLLM()
nlp_processor = NL2Query(db, llm_generator)
question = input("Write your question: ")

table_name, field, target_query = nlp_processor.understand_query(question)

if table_name:
    try:
        data = db.query(table_name, field, target_query)
    except:
        print(f"Runnning: {target_query}\n\n Failed")
