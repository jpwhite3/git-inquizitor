import base64
import io
import warnings
from collections import defaultdict
from datetime import datetime
from typing import List

import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")
plt.rcParams["figure.autolayout"] = True


def pie_chart(labels: List[str], data: List[int], title: str = None):
    plt.rcParams["figure.figsize"] = [4.00, 4.00]
    fig = plt.figure()
    ax1 = fig.add_subplot()
    if title:
        ax1.set_title(title)

    patches, texts, pcts = ax1.pie(
        data,
        labels=labels,
        autopct="%1.1f%%",
        wedgeprops={"linewidth": 1.0, "edgecolor": "white"},
        textprops={"size": "x-small", "fontweight": "bold"},
    )
    for i, patch in enumerate(patches):
        texts[i].set_color(patch.get_facecolor())
    plt.setp(pcts, color="white")
    plt.setp(texts, fontweight=600)
    plt.tight_layout()

    # Save the figure to a BytesIO object
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)

    # Convert the image to base64 encoding
    image_base64 = base64.b64encode(buffer.getvalue()).decode()

    return image_base64


def commit_graph(commits):
    plt.rcParams["figure.figsize"] = [10.00, 4.00]
    fig, ax = plt.subplots()

    # Extract dates and count commits for each date
    commit_dates = defaultdict(int)
    for commit in commits:
        commit_date = datetime.strptime(commit["date"].strftime("%Y-%m-%d"), "%Y-%m-%d")
        commit_dates[commit_date] += 1

    # Convert data to lists for plotting
    dates, commit_counts = zip(*sorted(commit_dates.items()))

    # Generate chart
    ax.plot(dates, commit_counts, label="Commits / Day")
    ax.fill_between(dates, commit_counts, alpha=0.3)
    # ax.set_xlabel("Time Period")
    # ax.set_ylabel("Count")
    ax.set_title("Commits / Time")
    ax.legend(loc="upper left", reverse=True)

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha="right")

    # Save the figure to a BytesIO object
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)

    # Convert the image to base64 encoding
    image_base64 = base64.b64encode(buffer.getvalue()).decode()

    return image_base64


def change_graph(commits):
    plt.rcParams["figure.figsize"] = [10.00, 4.00]
    fig, ax = plt.subplots()

    # Extract dates and count changes for each date
    insertion_counter = defaultdict(int)
    deletion_counter = defaultdict(int)
    for commit in commits:
        commit_date = datetime.strptime(commit["date"].strftime("%Y-%m-%d"), "%Y-%m-%d")
        insertion_counter[commit_date] += commit["insertions"]
        deletion_counter[commit_date] += commit["deletions"] * -1

    # Convert data to lists for plotting
    insertion_dates, insertion_counts = zip(*sorted(insertion_counter.items()))
    deletion_dates, deletion_counts = zip(*sorted(deletion_counter.items()))

    # Generate chart
    ax.plot(
        insertion_dates, insertion_counts, color="green", label="Inserted Lines / Day"
    )
    ax.plot(deletion_dates, deletion_counts, color="red", label="Deleted Lines / Day")
    ax.fill_between(
        insertion_dates,
        insertion_counts,
        color="green",
        alpha=0.3,
    )
    ax.fill_between(
        deletion_dates,
        deletion_counts,
        color="red",
        alpha=0.3,
    )
    # ax.set_xlabel("Time Period")
    # ax.set_ylabel("Lines")
    ax.set_title("Line changes / Time")
    ax.legend(loc="upper left", reverse=True)

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha="right")

    # Save the figure to a BytesIO object
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)

    # Convert the image to base64 encoding
    image_base64 = base64.b64encode(buffer.getvalue()).decode()

    return image_base64
