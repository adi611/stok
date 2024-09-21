import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()


@dataclass
class Story:
    title: str
    time: str
    url: str


class Scraper(ABC):
    @abstractmethod
    def scrape(self) -> List[Story]:
        pass


class WebsiteScraper(Scraper):
    def __init__(self, url: str):
        self.base_url = url

    def scrape(self) -> List[Story]:
        response = requests.get(self.base_url)
        soup = BeautifulSoup(response.text, "html.parser")
        story_divs = soup.select(
            "body main.pageHolder div.main_container section.section_list div.tabdata div.eachStory"
        )

        stories = []
        for div in story_divs:
            title = div.find("h3").find("a").text.strip()
            time = div.find("time").text.strip()
            url = div.find("h3").find("a")["href"]
            full_url = f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"
            stories.append(Story(title, time, full_url))

        return stories


class StoryFilter:
    @staticmethod
    def filter_stories(stories: List[Story], keywords: List[str]) -> List[Story]:
        return [
            story
            for story in stories
            if any(keyword in story.title.lower() for keyword in keywords)
        ]


class MessageSender(ABC):
    @abstractmethod
    def send_message(self, story: Story) -> bool:
        pass


class WhatsAppTemplateSender(MessageSender):
    def __init__(
        self,
        app_id: str,
        app_secret: str,
        phone_number_id: str,
        recipient_waid: str,
        template_name: str,
        language_code: str,
        access_token: str,
    ):
        self.app_id = app_id
        self.app_secret = app_secret
        self.phone_number_id = phone_number_id
        self.recipient_waid = recipient_waid
        self.template_name = template_name
        self.language_code = language_code
        self.access_token = access_token

    def send_message(self, story: Story) -> bool:
        url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        data = {
            "messaging_product": "whatsapp",
            "to": self.recipient_waid,
            "type": "template",
            "template": {
                "name": self.template_name,
                "language": {"code": self.language_code},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": story.title},
                            {"type": "text", "text": story.time},
                        ],
                    },
                    {
                        "type": "button",
                        "sub_type": "url",
                        "index": "0",
                        "parameters": [{"type": "text", "text": story.url}],
                    },
                ],
            },
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            print(f"Error sending message: {response.status_code}, {response.text}")
        return response.status_code == 200


class StoryProcessor:
    def __init__(self, scraper: Scraper, filter: StoryFilter, sender: MessageSender):
        self.scraper = scraper
        self.filter = filter
        self.sender = sender

    def process(self, keywords: List[str]):
        stories = self.scraper.scrape()
        filtered_stories = self.filter.filter_stories(stories, keywords)

        for story in filtered_stories:
            if self.sender.send_message(story):
                print(f"Message sent successfully for story: {story.title}")
                break
            else:
                print(f"Failed to send message for story: {story.title}")


def main():
    url = os.getenv("WEBSITE_URL")
    app_id = os.getenv("APP_ID")
    app_secret = os.getenv("APP_SECRET")
    phone_number_id = os.getenv("PHONE_NUMBER_ID")
    recipient_waid = os.getenv("RECIPIENT_WAID")
    template_name = os.getenv("TEMPLATE_NAME", "payment_failed_3 ")
    language_code = os.getenv("LANGUAGE_CODE", "en_US")
    access_token = os.getenv("ACCESS_TOKEN", "")

    scraper = WebsiteScraper(url)
    filter = StoryFilter()
    sender = WhatsAppTemplateSender(
        app_id,
        app_secret,
        phone_number_id,
        recipient_waid,
        template_name,
        language_code,
        access_token,
    )
    processor = StoryProcessor(scraper, filter, sender)

    processor.process(keywords=["sebi", "split", "market"])


if __name__ == "__main__":
    main()
