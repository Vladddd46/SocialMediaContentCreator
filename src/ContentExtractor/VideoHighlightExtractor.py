import os
import re

import moviepy.editor as mp
import whisper
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import pipeline


class VideoHighlightExtractor:
    def __init__(self, model_name="base", sentiment_model="xlm-roberta-base"):
        # Load Whisper model and multilingual sentiment analyzer
        self.model = whisper.load_model(model_name)
        self.sentiment_analyzer = pipeline("sentiment-analysis", model=sentiment_model)

        # Set environment variable to avoid parallelism warnings
        os.environ["TOKENIZERS_PARALLELISM"] = "false"

        # Keywords for scoring informativeness (English, Russian, Ukrainian)
        self.informative_keywords = {
            "en": [
                "because",
                "explain",
                "history",
                "facts",
                "results",
                "data",
                "analysis",
                "study",
                "experience",
                "importance",
                "lesson",
                "meaning",
                "context",
                "details",
                "further steps",
                "research",
                "development",
                "strategy",
            ],
            "ru": [
                "потому что",
                "объясню",
                "история",
                "факты",
                "результаты",
                "данные",
                "анализ",
                "изучение",
                "опыт",
                "важность",
                "урок",
                "смысл",
                "контекст",
                "подробности",
                "дальнейшие шаги",
                "исследования",
                "развитие",
                "стратегия",
            ],
            "uk": [
                "тому що",
                "поясню",
                "історія",
                "факти",
                "результати",
                "дані",
                "аналіз",
                "дослідження",
                "досвід",
                "важливість",
                "урок",
                "значення",
                "контекст",
                "деталі",
                "подальші кроки",
                "розвиток",
                "стратегія",
            ],
        }
        self.unwanted_keywords = {
            "en": [
                "buy",
                "discount",
                "order",
                "online shop",
                "visit website",
                "purchase",
            ],
            "ru": [
                "купить",
                "скидка",
                "заказать",
                "онлайн магазин",
                "перейдите на сайт",
                "покупка",
            ],
            "uk": [
                "купити",
                "знижка",
                "замовити",
                "онлайн магазин",
                "перейдіть на сайт",
                "покупка",
            ],
        }

    def get_highlights(
        self,
        source_path,
        highlights_path,
        max_highlights=15,
        max_duration=60,
        context_buffer=5,
    ):
        print("Loading video...")
        video = self._load_video(source_path)

        print("Transcribing audio...")
        transcript, detected_language = self._transcribe_audio(source_path)

        print(f"Detected language: {detected_language}")
        print("Segmenting into Q&A pairs...")
        qa_pairs = self._segment_into_qa_pairs(transcript)

        print("Analyzing and scoring informativeness for answers...")
        scored_segments = self._analyze_and_score_informativeness(
            qa_pairs, detected_language
        )

        print("Selecting highlights based on informativeness scores...")
        highlights = self._select_highlights_by_info(scored_segments, max_highlights)

        print(f"Extracting {len(highlights)} highlights...")
        self._extract_highlights(
            video, highlights, transcript, highlights_path, max_duration, context_buffer
        )

        print(f"Highlights saved to folder: {highlights_path}")

    def _load_video(self, video_path):
        return mp.VideoFileClip(video_path)

    def _transcribe_audio(self, video_path):
        result = self.model.transcribe(
            video_path, language=None
        )  # Auto-detect language
        return result["text"], result.get(
            "language", "en"
        )  # Return transcript and detected language

    def _segment_into_qa_pairs(self, transcript):
        qa_pairs = []
        sentences = re.split(r"(?<=[.!?]) +", transcript)

        current_question = None
        current_answer = ""
        for sentence in sentences:
            if sentence.endswith("?") or len(sentence.split()) < 10:
                if current_question and current_answer:
                    qa_pairs.append((current_question.strip(), current_answer.strip()))
                current_question = sentence.strip()
                current_answer = ""
            elif current_question:
                current_answer += " " + sentence.strip()

        if current_question and current_answer:
            qa_pairs.append((current_question.strip(), current_answer.strip()))

        print(f"Found {len(qa_pairs)} question-answer pairs.")
        return qa_pairs

    def _analyze_and_score_informativeness(self, qa_pairs, language, max_length=512):
        scored_segments = []
        informative_keywords = self.informative_keywords.get(
            language, self.informative_keywords["en"]
        )
        unwanted_keywords = self.unwanted_keywords.get(
            language, self.unwanted_keywords["en"]
        )

        # Common phrases that indicate general, less informative content
        intro_phrases = [
            "welcome to my channel",
            "hello everyone",
            "thank you for joining us",
            "glad to have you here",
            "let's get started",
            "subscribe",
            "hit the like button",
        ]

        for question, answer in qa_pairs:
            truncated_question = question[:max_length]
            truncated_answer = answer[:max_length]

            sentiment_q = self.sentiment_analyzer(truncated_question)[0]
            sentiment_a = self.sentiment_analyzer(truncated_answer)[0]

            combined_score = max(sentiment_q["score"], sentiment_a["score"])
            info_score = combined_score

            # Check for informative keywords
            informative_match = any(
                keyword.lower() in truncated_answer.lower()
                for keyword in informative_keywords
            )
            unwanted_match = any(
                keyword.lower() in truncated_answer.lower()
                for keyword in unwanted_keywords
            )
            intro_match = any(
                phrase.lower() in truncated_answer.lower() for phrase in intro_phrases
            )

            # Adjust score based on matches
            if informative_match:
                info_score += 0.7

            if unwanted_match:
                info_score -= 1.0

            # Penalize segments that match common introductory phrases
            if intro_match:
                info_score -= 1.5

            # Only include segments that have a reasonably positive sentiment and are not marked unwanted
            if combined_score >= 0.2 and not unwanted_match:
                scored_segments.append(
                    (question, answer, info_score, informative_match)
                )

        return scored_segments

    def _select_highlights_by_info(self, scored_segments, max_highlights):
        # Sort segments by informativeness score in descending order
        scored_segments.sort(key=lambda x: x[2], reverse=True)
        highlights = scored_segments[:max_highlights]

        print(
            f"Selected {len(highlights)} highlights based on informativeness scores, sorted by interest."
        )
        return highlights

    def _extract_highlights(
        self, video, highlights, transcript, output_folder, max_duration, context_buffer
    ):
        os.makedirs(output_folder, exist_ok=True)

        for idx, (question, answer, info_score, informative_match) in enumerate(
            highlights
        ):
            q_start = transcript.find(question)
            a_start = transcript.find(answer, q_start)
            a_end = a_start + len(answer)

            start_time = (q_start / len(transcript)) * video.duration
            end_time = (a_end / len(transcript)) * video.duration

            # Add context buffer before and after the highlight
            start_time = max(start_time - context_buffer, 0)
            end_time = min(end_time + context_buffer, video.duration)

            if end_time - start_time > max_duration:
                end_time = start_time + max_duration

            clip = video.subclip(start_time, end_time)
            clip = clip.set_audio(video.audio.subclip(start_time, end_time))

            output_path = os.path.join(output_folder, f"highlight_{idx + 1}.mp4")

            clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
            print(f"Saved highlight {idx + 1} to {output_path}")

    def generate_hashtags(self, highlight_path, max_hashtags=10):
        """
        Generate a list of hashtags based on the content of a video highlight.

        :param highlight_path: Path to the video highlight.
        :param max_hashtags: Maximum number of hashtags to generate.
        :return: A string of hashtags for TikTok.
        """
        print("Transcribing highlight for hashtag generation...")
        transcript, _ = self._transcribe_audio(highlight_path)

        print("Extracting key phrases...")
        keywords = self._extract_keywords(transcript)

        # Create hashtags by adding a '#' before each keyword and replacing spaces with underscores
        hashtags = [
            f"#{keyword.replace(' ', '_')}" for keyword in keywords[:max_hashtags]
        ]

        # Join hashtags into a single string suitable for TikTok
        hashtags_string = " ".join(hashtags)

        print(f"Generated hashtags: {hashtags_string}")
        return hashtags_string

    def _extract_keywords(self, text, max_features=20):
        """
        Extract key phrases from the text using TF-IDF.

        :param text: Text from which to extract key phrases.
        :param max_features: Maximum number of features to consider for TF-IDF.
        :return: List of keywords sorted by importance.
        """
        # Preprocess text: remove punctuation, convert to lowercase
        text = re.sub(r"[^\w\s]", "", text.lower())

        # Use TF-IDF to extract keywords
        vectorizer = TfidfVectorizer(max_features=max_features, stop_words="english")
        tfidf_matrix = vectorizer.fit_transform([text])

        # Extract feature names and their corresponding scores
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.toarray().flatten()

        # Sort features by their scores in descending order
        sorted_keywords = sorted(
            zip(feature_names, scores), key=lambda x: x[1], reverse=True
        )
        keywords = [keyword for keyword, score in sorted_keywords]

        return keywords
