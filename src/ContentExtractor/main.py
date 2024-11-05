import os
import moviepy.editor as mp
import whisper
from transformers import pipeline
import re

# Set environment variable to avoid parallelism warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"


# Step 1: Load the interview video
def load_video(video_path):
    video = mp.VideoFileClip(video_path)
    return video


# Step 2: Transcribe audio using Whisper
def transcribe_audio(video_path):
    model = whisper.load_model("base")
    result = model.transcribe(video_path)
    print(result["text"])
    exit(1)
    return result["text"]


# Step 3: Segment into Q&A pairs using structured heuristics
def segment_into_qa_pairs(transcript):
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


# Step 4: Analyze the sentiment and score for informativeness
def analyze_and_score_informativeness(qa_pairs, max_length=512):
    sentiment_analyzer = pipeline(
        "sentiment-analysis", model="cointegrated/rubert-tiny-sentiment-balanced"
    )
    informative_keywords = [
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
    ]
    unwanted_keywords = [
        "купить",
        "скидка",
        "заказать",
        "онлайн магазин",
        "перейдите на сайт",
        "покупка",
    ]
    scored_segments = []

    for question, answer in qa_pairs:
        truncated_question = question[:max_length]
        truncated_answer = answer[:max_length]

        # Analyze sentiment of both question and answer
        sentiment_q = sentiment_analyzer(truncated_question)[0]
        sentiment_a = sentiment_analyzer(truncated_answer)[0]

        combined_score = max(sentiment_q["score"], sentiment_a["score"])
        info_score = combined_score

        informative_match = any(
            keyword.lower() in truncated_answer.lower()
            for keyword in informative_keywords
        )
        unwanted_match = any(
            keyword.lower() in truncated_answer.lower() for keyword in unwanted_keywords
        )

        if informative_match:
            info_score += 0.7

        if unwanted_match:
            info_score -= 1.0

        if combined_score >= 0.2 and not unwanted_match:
            scored_segments.append((question, answer, info_score, informative_match))

    return scored_segments


# Step 5: Sort and filter segments by informativeness score
def select_highlights_by_info(scored_segments, max_highlights=15):
    scored_segments.sort(key=lambda x: x[2], reverse=True)
    highlights = scored_segments[:max_highlights]
    print(f"Selected {len(highlights)} highlights based on informativeness scores.")
    return highlights


# Step 6: Extract each highlight (question + answer) as a video file with a duration limit
def extract_highlights(
    video, highlights, transcript, output_folder="highlights", max_duration=60
):
    os.makedirs(output_folder, exist_ok=True)

    for idx, (question, answer, info_score, informative_match) in enumerate(highlights):
        q_start = transcript.find(question)
        a_start = transcript.find(answer, q_start)
        a_end = a_start + len(answer)

        start_time = (q_start / len(transcript)) * video.duration
        end_time = (a_end / len(transcript)) * video.duration

        if end_time - start_time > max_duration:
            end_time = start_time + max_duration

        clip = video.subclip(max(start_time, 0), end_time)
        clip = clip.set_audio(video.audio.subclip(max(start_time, 0), end_time))

        output_path = os.path.join(output_folder, f"highlight_{idx + 1}.mp4")

        clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
        print(f"Saved highlight {idx + 1} to {output_path}")


# Main function to process the video and save highlights
def main(video_path, output_folder="highlights", max_highlights=15, max_duration=60):
    print("Loading video...")
    video = load_video(video_path)

    print("Transcribing audio...")
    transcript = transcribe_audio(video_path)

    print("Segmenting into Q&A pairs...")
    qa_pairs = segment_into_qa_pairs(transcript)

    print("Analyzing and scoring informativeness for answers...")
    scored_segments = analyze_and_score_informativeness(qa_pairs)

    print("Selecting highlights based on informativeness scores...")
    highlights = select_highlights_by_info(scored_segments, max_highlights)

    print(f"Extracting {len(highlights)} highlights...")
    extract_highlights(video, highlights, transcript, output_folder, max_duration)

    print(f"Highlights saved to folder: {output_folder}")


# Example usage
if __name__ == "__main__":
    video_path = "test2.mp4"
    output_folder = "highlights"
    main(video_path, output_folder)
