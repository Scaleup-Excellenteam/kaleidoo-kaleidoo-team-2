from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from transformers import AutoTokenizer, AutoModel
import torch
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Connect to Milvus
def connect_to_milvus():
    public_endpoint = os.getenv('PUBLIC_ENDPOINT')
    token = os.getenv('TOKEN')

    connections.connect(
        alias="default", 
        uri=f"{public_endpoint}",  
        token=token  
    )
    print("Connected to Milvus Cloud!")

# Load AlephBERT tokenizer and model for embedding
tokenizer = AutoTokenizer.from_pretrained("onlplab/alephbert-base")
model = AutoModel.from_pretrained("onlplab/alephbert-base")

def embed_text(text):
    """
    Converts input text into embeddings using AlephBERT.
    
    Parameters:
    - text (str): Input text to embed.
    
    Returns:
    - embeddings (list of float): Embeddings of the input text as a flat list of floats.
    """
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    
    embeddings = outputs.last_hidden_state[:, 0, :].flatten().tolist()
    return embeddings

def create_milvus_collection(collection_name):
    """
    Creates a Milvus collection with the schema if it doesn't exist.
    
    Parameters:
    - collection_name (str): The name of the Milvus collection.
    """
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
        FieldSchema(name="file_path", dtype=DataType.VARCHAR, max_length=500)
    ]
    schema = CollectionSchema(fields, description="Lecture materials embeddings collection")

    if not utility.has_collection(collection_name):
        collection = Collection(name=collection_name, schema=schema)
        print(f"Collection '{collection_name}' created successfully!")
    else:
        collection = Collection(name=collection_name)
        print(f"Collection '{collection_name}' already exists.")
    
    return collection

def store_single_data_in_milvus(collection_name, hebrew_text, file_path):
    """
    Stores a single Hebrew text embedding and corresponding file path in Milvus.
    
    Parameters:
    - collection_name (str): The name of the Milvus collection.
    - hebrew_text (str): A single Hebrew text to embed.
    - file_path (str): The corresponding file path.
    """
    connect_to_milvus()

    collection = create_milvus_collection(collection_name)

    # Convert the single Hebrew text to an embedding
    embedding = embed_text(hebrew_text)
    
    # Insert the embedding and file path into Milvus
    collection.insert([[embedding], [file_path]])  # Insert single embedding and file path
    print(f"Inserted 1 record into the collection '{collection_name}'.")

    # Flush the collection to persist data
    collection.flush()  # Force flush to ensure data is saved
    print("Collection flushed successfully!")

    # Create index for efficient search
    create_index_on_embeddings(collection_name)

    # Reload the collection and check the number of records
    collection.load()
    print(f"Number of records after flush: {collection.num_entities}")


def store_data_in_milvus(collection_name, hebrew_texts, file_paths):
    """
    Stores Hebrew text embeddings and file paths in Milvus.
    
    Parameters:
    - collection_name (str): The name of the Milvus collection.
    - hebrew_texts (list): List of Hebrew texts.
    - file_paths (list): List of corresponding file paths.
    """
    connect_to_milvus()

    collection = create_milvus_collection(collection_name)

    # Convert texts to embeddings
    embeddings = [embed_text(text) for text in hebrew_texts]
    
    # Insert embeddings and file paths into Milvus
    collection.insert([embeddings, file_paths])
    print(f"Inserted {len(embeddings)} records into the collection '{collection_name}'.")

    # Flush the collection to persist data
    collection.flush()  # Force flush to ensure data is saved
    print("Collection flushed successfully!")

    # Create index for efficient search
    create_index_on_embeddings(collection_name)

    # Reload the collection and check number of records
    collection.load()
    print(f"Number of records after flush: {collection.num_entities}")


def create_index_on_embeddings(collection_name):
    """
    Creates an index on the 'embedding' field in the specified Milvus collection.
    
    Parameters:
    - collection_name (str): The name of the collection to create an index on.
    """
    collection = Collection(collection_name)

    index_params = {
        "metric_type": "L2",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 128},
    }

    print(f"Creating index on 'embedding' field in collection '{collection_name}'...")
    collection.create_index(field_name="embedding", index_params=index_params)
    print("Index created successfully!")

def main():
    hebrew_texts = [
    "הנדסת מחשבים היא תחום הנדסי העוסק בתכנון, פיתוח, ובנייה של מערכות מחשוב. תחום זה כולל את הבנת פעולתם של מעבדים, זיכרונות, ואמצעי קלט פלט, לצד הפיתוח של תוכנה שתומכת בפעולתם. הנדסת מחשבים דורשת ידע רחב בטכנולוגיות החומרה והתוכנה, ומטרתה היא ליצור מערכות יעילות, אמינות, ובטוחות. מעבר לפיתוח החומרה עצמה, הנדסת מחשבים כוללת גם נושאים כמו אלגוריתמים מקביליים, עיבוד אותות דיגיטליים, ומערכות משובצות מחשב. תחום זה משתלב בתחומים אחרים כמו הנדסת אלקטרוניקה ומדעי המחשב, ונחשב לאחד התחומים המתקדמים בעולם הטכנולוגיה.",

    "הנדסת תוכנה היא תחום העוסק בפיתוח תוכנות מחשב, תוך שימוש בשיטות הנדסיות שמטרתן להבטיח איכות, אמינות, ותחזוקה ארוכת טווח של התוכנה. הנדסת תוכנה משלבת ידע בתכנות, תכנון מערכות, בדיקות תוכנה, ואבטחת מידע, והיא עוסקת בפיתוח מוצרי תוכנה מכל הסוגים – ממערכות קטנות ועד פרויקטים מורכבים ורחבי היקף. מהנדסי תוכנה אחראים להגדיר את הדרישות הפונקציונליות של המערכת, לתכנן את הארכיטקטורה שלה, ולבצע אינטגרציה בין רכיבי תוכנה שונים. תחום זה מצריך יכולות אנליטיות גבוהות ויכולת לעבוד בצוותים על פרויקטים גדולים.",

    "טכנולוגיות חדשות מופיעות באופן מתמיד ומשנות את הדרך שבה אנו מתקשרים, עובדים ולומדים. עם התקדמות מדהימה בתחומים כמו בינה מלאכותית, רובוטיקה, מחשוב קוונטי, וביוטכנולוגיה, תחומים טכנולוגיים חדשים מאתגרים את הגבולות של הידע האנושי. בעזרת טכנולוגיות מתקדמות ניתן לשפר את הבריאות, לשדרג תשתיות, ולהגביר את היעילות בתהליכים תעשייתיים. טכנולוגיות אלה מביאות עימן אתגרים חדשים שקשורים לאתיקה, אבטחת מידע, פרטיות, ושינויי אקלים, ולכן הן דורשות הבנה מעמיקה ורחבה כדי להבטיח יישום אחראי ומוסרי בעולם המודרני.",

    "לימודי נתונים הם תחום דינמי הנוגע באיסוף, ניתוח, ועיבוד כמויות גדולות של נתונים ממקורות שונים. בעידן המידע הנוכחי, הנתונים הפכו לאחד המשאבים החשובים ביותר, ותחום לימודי הנתונים מתמקד בהפקת תובנות שימושיות מנתונים גולמיים. לימודים אלה כוללים ידע בתכנות, סטטיסטיקה, אלגוריתמים של למידת מכונה, ועבודה עם מאגרי נתונים. המטרה המרכזית היא לשפר תהליכי קבלת החלטות במגוון תחומים כמו בריאות, תעשייה, מדע, וכלכלה. כישוריהם של מדעני נתונים הם ביקורתיים ביותר בעולם הטכנולוגי של היום.",

    "מדעי המחשב הם תחום מחקר העוסק בתיאוריה וביישום של מערכות מחשוב. התחום כולל תיאוריה של אלגוריתמים, מדעי הנתונים, עיבוד תמונה, ניתוח נתונים, פיתוח מערכות הפעלה, עיצוב רשתות מחשבים, ועוד. מדעי המחשב עוסקים גם בפיתוח טכנולוגיות חדשות שנמצאות בבסיס מערכות המידע המודרניות. התחום דורש ידע מתמטי נרחב ויכולת לפתח פתרונות לבעיות מורכבות בתחום התוכנה והחומרה. מדעי המחשב ממשיכים להשפיע על מגוון תחומים אחרים, כולל בינה מלאכותית, רובוטיקה, ותעשיית המידע, ומהווים את הבסיס לפיתוחים טכנולוגיים מהפכניים.",

    "עיצוב גרפי הוא תחום אומנותי וטכנולוגי המתמקד בהעברת מסרים דרך אלמנטים חזותיים כמו תמונות, טקסט, וצורות. מעצבים גרפיים משתמשים בתוכנות כמו פוטושופ ואילוסטרייטור כדי ליצור לוגואים, פרסומות, ממשקים לאפליקציות ואתרי אינטרנט. מעבר לכישורי עיצוב, על מעצב גרפי להבין את מטרות הלקוח ואת הצרכים השיווקיים כדי ליצור עיצובים מותאמים ומדויקים. עיצוב גרפי משתלב בתחומים כמו עיצוב חוויית משתמש, פרסום, והדפסה. תחום זה דורש שילוב של יצירתיות, ידע טכנולוגי, ויכולת לעבוד עם צוותים בפרויקטים משותפים.",

    "הנדסת בניין היא תחום הנדסי המתמקד בתכנון ובניית מבנים ותשתיות כמו גשרים, כבישים, ומבנים רבי קומות. מהנדסי בניין אחראים על הבטיחות, היציבות, והעמידות של המבנים, תוך שימוש בטכנולוגיות בנייה מתקדמות ובחומרים עמידים. הנדסת בניין כוללת תכנון מבנים לפי תקנים מחמירים וביצוע בדיקות קפדניות כדי להבטיח שהמבנה יהיה עמיד לאורך זמן. בנוסף, התחום משלב עבודה עם תוכנות מחשב לתכנון מבנים ובדיקת חוזקם. הנדסת בניין היא תחום חשוב וחיוני במערך הפיתוח התשתיתי והעירוני של כל מדינה בעולם.",

    "הנדסת חשמל היא תחום מדעי והנדסי המתמקד בלימוד ייצור, הולכה, ושימוש בחשמל. מהנדסי חשמל עוסקים בתכנון מערכות חשמליות, פיתוח רכיבים אלקטרוניים, תכנון מערכות תקשורת, ועוד. תחום זה כולל גם את יישום חוקי הפיזיקה והמתמטיקה במערכות אלקטרומגנטיות ואנרגיה. הנדסת חשמל מהווה בסיס לפיתוחים טכנולוגיים בתחומים כמו תקשורת סלולרית, מחשבים, ורובוטיקה. מהנדסי חשמל נדרשים לשלב ידע תיאורטי נרחב עם יכולת לפתח פתרונות טכנולוגיים מתקדמים שיבטיחו יציבות וביצועים גבוהים של מערכות חשמל ואלקטרוניקה.",

    "מחשוב ענן הוא תחום טכנולוגי מתקדם המאפשר גישה לשירותי מחשוב דרך האינטרנט. תחום זה כולל איחסון נתונים, עיבוד חישובי, ושרתי אירוח מרוחקים המסופקים על ידי ספקי ענן. מחשוב ענן מאפשר לארגונים להפעיל מערכות מורכבות ונתוני עתק ללא צורך בתשתיות פיזיות יקרות. בנוסף, הוא מאפשר גמישות תפעולית רבה יותר וגישה לנתונים מכל מקום בעולם. מחשוב ענן משתלב בתחומים כמו ניהול מסדי נתונים, פיתוח אפליקציות, ובינה מלאכותית. תחום זה ממשיך לצמוח במהירות, והוא חלק בלתי נפרד מהטכנולוגיה המודרנית של ימינו.",

    "בינה מלאכותית היא תחום במדעי המחשב המתמקד בפיתוח מערכות שיכולות לבצע משימות הדורשות אינטליגנציה אנושית. דוגמאות לכך כוללות זיהוי תמונות, עיבוד שפה טבעית, וקבלת החלטות מורכבות. בעזרת בינה מלאכותית ניתן לפתח מערכות שמסוגלות ללמוד מנתונים, לבצע תחזיות, ולהתאים את עצמן לסביבות משתנות. טכנולוגיות כמו למידת מכונה ורשתות נוירונים הן חלק בלתי נפרד מתחום הבינה המלאכותית. התחום משפיע על מגוון רחב של תעשיות, כולל תחום הבריאות, תחבורה, ואפילו אמנות. בינה מלאכותית מהווה את אחת ההתפתחויות המרגשות והמשפיעות ביותר בעולם הטכנולוגי."
]


    file_paths = [
        "/path/to/file1",
        "/path/to/file2",
        "/path/to/file3",
        "/path/to/file4",
        "/path/to/file5",
        "/path/to/file6",
        "/path/to/file7",
        "/path/to/file8",
        "/path/to/file9",
        "/path/to/file10"
    ]
    
    store_data_in_milvus("lecture_materials_embeddings", hebrew_texts, file_paths)

if __name__ == "__main__":
    main()
