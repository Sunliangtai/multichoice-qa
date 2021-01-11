import six
import unicodedata


def process_text(inputs, remove_space=True, lower=False):
    """preprocess data by removing extra space and normalize data."""
    outputs = inputs
    if remove_space:
        outputs = " ".join(inputs.strip().split())

    if six.PY2 and isinstance(outputs, str):
        try:
            outputs = six.ensure_text(outputs, "utf-8")
        except UnicodeDecodeError:
            outputs = six.ensure_text(outputs, "latin-1")

    outputs = unicodedata.normalize("NFKD", outputs)
    outputs = "".join([c for c in outputs if not unicodedata.combining(c)])
    if lower:
        outputs = outputs.lower()

    return outputs


# Preprocessing the datasets.
def prepare_features(examples, tokenizer=None, data_args=None):
    dialogues = examples['dialogue']
    answers = examples['answer']
    options = examples['choice']
    questions = examples['question']

    labels = []
    qa_list = []
    processed_contexts = []

    for i in range(len(answers)):
        label = options[i].index(answers[i])
        labels.append(label)
        dialogue = dialogues[i]
        context = ""
        for d in dialogue:
            context += d
        processed_contexts.append([process_text(context)] * 3)

        question = process_text(questions[i])
        qa_pairs = []
        for j in range(3):
            option = process_text(options[i][j])

            if "_" in question:
                qa_cat = question.replace("_", option)
            else:
                qa_cat = " ".join([question, option])
            qa_pairs.append(qa_cat[- data_args.max_qa_length:])
        qa_list.append(qa_pairs)

    first_sentences = sum(processed_contexts, [])
    second_sentences = sum(qa_list, [])

    tokenized_examples = tokenizer(
        first_sentences,
        second_sentences,
        truncation="only_first",
        max_length=data_args.max_seq_length,
        padding="max_length" if data_args.pad_to_max_length else False,
    )
    tokenized_examples = {k: [v[i: i + 3] for i in range(0, len(v), 3)] for k, v in tokenized_examples.items()}

    tokenized_examples['label'] = labels

    # Un-flatten
    return tokenized_examples
