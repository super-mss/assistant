import os;
from openai import OpenAI

openai_api_key = "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"
client = OpenAI(api_key=openai_api_key)

file = "KOBIS.pdf"
def file_upload(file) :
    file = client.files.create(
        file = open(file,"rb"),
        purpose="assistants"
    )
    return file.id


file_id = file_upload(file)

def assistant_creator() :
    my_assistant = client.beta.assistants.create(
        instructions="당신은 유능한 비서입니다. 제공한 파일에 접근 할 권한이 있으며 대답은 한국어를 사용합니다. 파일에는 2023년 한국에서 개봉한 영화 정보가 1위부터 50위까지 순서대로 기록되어 있습니다. 각 행은 5칸으로 되어있는데 순위, 영화명, 개봉일, 매출액, 매출액 점유율 순서로 되어 있습니다. 예를 들어 순위에 해당하는 칸에 15라고 적여있으면 그 칸이 포함된 행에 정보가 15위 영화에 대한 정보입니다.",
        name = "movie bot",
        tools=[{"type": "retrieval"}],
        model="gpt-3.5-turbo-1106",
        file_ids=[file_id],

    )
    print(my_assistant.id)


assistant_creator()

