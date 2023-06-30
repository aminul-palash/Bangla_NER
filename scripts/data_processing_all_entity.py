import json
import argparse
from transformers import BasicTokenizer
from spacy.training.iob_utils import iob_to_biluo



class IOBProcess:
    """Class for processing IOB-formatted data."""

    def __init__(self):
        self.valid_iob_entity = {"I-PER", "O", "B-PER"}

    def read_file_lines(self, filename):
        """
        Read lines from a file.

        Args:
            filename (str): The path to the file.

        Returns:
            list: The list of lines read from the file.
        """
        lines = []
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                lines.append(line)
        return lines

    def clean_iob_data(self, file_path):
        """
        Clean and process IOB-formatted data.

        Args:
            file_path (str): The path to the input file.

        Returns:
            list: The processed IOB-formatted data.
        """
        data = self.read_file_lines(file_path)
        unique_tags = set()
        iob_data = []
        for line in data:
            line = line.strip('\n')
            if not line or len(line.split('\t')) != 2:
                iob_data.append('\n')
                continue

            text, tag = line.split('\t')
            if text and tag:
                text = text.replace('\ufeff', '')
                unique_tags.add(tag)
                # if tag not in self.valid_iob_entity:
                #     tag = 'O'
                iob_data.append(text + '\t' + tag)
        
        return iob_data


class IobToJSONbiluo:
    def __init__(self):
        """
        Initializes the IobToJSONbiluo class.
        """
        self.valid_biluo_entity_tags = {'O', 'I-PER', 'B-PER', 'U-PER', 'L-PER'}

    def remove_non_entity_sentences(self, data):
        """
        Removes sentences that do not contain any named entity tags from the provided data.

        Args:
            data (list): The input data in JSON format.

        Returns:
            list: The filtered data containing sentences with named entity tags.
        """
        token_o = 0
        token_per = 0
        data_contain_at_list_one_name_tag = []
        id_cnt = 0

        for d in data:
            sentence_tokens = d["paragraphs"][0]["sentences"][0]["tokens"]
            tags = set()
            for token in sentence_tokens:
                tags.add(token["ner"])

            if tags == set('O'):
                token_o += 1
            else:
                token_per += 1
                d['id'] = id_cnt
                data_contain_at_list_one_name_tag.append(d)
                id_cnt += 1

        # print(f"Total sentences that only contain 'O' tags: {token_o}")
        # print(f"Total sentences that only contain 'PER' tags: {token_per}")

        return data_contain_at_list_one_name_tag

    def convert_iob_to_biluo(self, file_path, output_path="data.json"):
        """
        Converts IOB format data to JSON biluo format.

        Args:
            file_path (str): The path to the input IOB file.
            output_path (str, optional): The path to save the output JSON file. Defaults to "data.json".
        """
        obj = IOBProcess()
        data = obj.clean_iob_data(file_path)
        
        spacy_json_data = []
        tokens = []
        data_id = 0

        for line in data:
            if line == '\n':
                if tokens:
                    tokens = self.change_entity_tags(tokens)
                    sentence_json_data = self.get_spacy_json_data_template(
                        id=data_id, tokens=tokens
                    )
                    spacy_json_data.append(sentence_json_data)
                    data_id += 1
               
                tokens = []
            else:
                line = line.strip('\n')
                text, tag = line.split('\t')
                tokens.append({
                    "orth": text,
                    "tag": "-",
                    "ner": tag
                })

        
        filtered_data = self.remove_non_entity_sentences(spacy_json_data)
        return filtered_data
        # with open(output_path, 'w') as fp:
        #     json.dump(filtered_data, fp, indent=2, ensure_ascii=False)
        #     print(f"File saved at: {output_path}")
        
    def get_spacy_json_data_template(self, id, tokens):
        """
        Creates the JSON data template for a single sentence.

        Args:
            id (int): The sentence ID.
            tokens (list): The list of tokens in the sentence.

        Returns:
            dict: The JSON data template for the sentence.
        """
        return {
            "id": id,
            "paragraphs": [{
                "sentences": [{
                    "tokens": tokens
                }]
            }]
        }

        
    def change_entity_tags(self, tokens):
        """
        Converts IOB format entity tags to biluo format for the provided tokens.

        Args:
            tokens (list): The list of tokens with IOB format entity tags.

        Returns:
            list: The list of tokens with biluo format entity tags.
        """
        token_ner_iob_tags = []
        for token in tokens:
            ner_tag = token['ner']
            token_ner_iob_tags.append(ner_tag)
        
        token_ner_biluo_tags = iob_to_biluo(token_ner_iob_tags)
        

        for token, biluo_tag in zip(tokens, token_ner_biluo_tags):
            token['ner'] = biluo_tag

        return tokens


class JsonlTobiluo(IobToJSONbiluo):
    """
    Converts data in JSONL format to biluo format for NER training.
    Inherits from the IobToJSONbiluo class.
    """

    def __init__(self):
        super().__init__()
        self.tokenizer = BasicTokenizer()
        self.valid_iob_entity = {'O', 'I-PER', 'B-PER', 'U-PER', 'L-PER'}

    def read_file_lines(self, filename):
        """
        Reads the lines from a text file.

        Args:
            filename (str): The path of the file to read.

        Returns:
            list: The lines of the file as a list.
        """
        lines = []
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                lines.append(line)
        return lines

    def remove_non_entity_sentences(self, data):
        """
        Removes sentences that do not contain any named entities.

        Args:
            data (list): The data in JSON format.

        Returns:
            list: The filtered data containing sentences with at least one named entity.
        """
        token_o = 0
        token_per = 0
        data_contain_at_least_one_name_tag = []
        id_cnt = 0
        
        for d in data:
            sentence_tokens = d["paragraphs"][0]["sentences"][0]["tokens"]
            tags = set()
            for token in sentence_tokens:
                tags.add(token["ner"])

            if tags == set('O'):
                token_o += 1
            else:
                token_per += 1
                d['id'] = id_cnt
                data_contain_at_least_one_name_tag.append(d)
                id_cnt += 1

        # print(f"Total sentences that only contain 'O' tags: {token_o}")
        # print(f"Total sentences that contain at least one `PER` tag: {token_per}")
        
        return data_contain_at_least_one_name_tag

    def format_json_data(self, data):
        """
        Formats the data into the expected JSON format for training with spaCy.

        Args:
            data (list): The data in IOB format.

        Returns:
            list: The formatted data in JSON format.
        """
        spacy_json_data = []
        data_id = 0

        for item in data:
            tokens = []
            for line in item:
                line = line.strip('\n')
                text, tag = line.split('\t')
                token = {
                    "orth": text,
                    "tag": "-",
                    "ner": tag
                }
                tokens.append(token)

            sentence_json_data = self.get_spacy_json_data_template(id=data_id, tokens=tokens)
            spacy_json_data.append(sentence_json_data)
            data_id += 1

        return spacy_json_data
    
    def convert_jsonl_to_biluo_json_format(self, file_path, output_path="test.json"):
        """
        Converts data in JSONL format to biluo format and saves it as a JSON file.

        Args:
            file_path (str): The path to the JSONL file.
            output_path (str, optional): The path to save the converted biluo JSON file. Defaults to "test.json".
        """
        data = self.read_file_lines(file_path)
        biluo_data = []
        unique_tags = set()
        miss_match_labels = 0

        for line in data:
            line = json.loads(line)
            text, labels = line[0], line[1]
            tokens = self.tokenizer.tokenize(text)

            # Skip data samples which have issues with token vs label tag
            if len(tokens) != len(labels):
                miss_match_labels += 1
                continue

            bilou_to_iob_labels = []
            for tag in labels:
                # Store unique tags
                unique_tags.add(tag)

                # Map PERSON with PER tag
                if 'PERSON' in tag:
                    tag = tag.replace('PERSON', 'PER')

                # if tag not in self.valid_iob_entity:
                #     tag = 'O'

                bilou_to_iob_labels.append(tag)

            sentences = [f"{token}\t{tag}" for token, tag in zip(tokens, bilou_to_iob_labels)]
            biluo_data.append(sentences)

        formatted_data = self.format_json_data(biluo_data)
        filtered_data = self.remove_non_entity_sentences(formatted_data)
        return filtered_data
        # print((filtered_data[0]))
        # print((filtered_data[len(filtered_data)-1]))
        # with open(output_path, 'w') as fp:
        #     json.dump(filtered_data, fp, indent=2, ensure_ascii=False)
        #     print(f"File saved at: {output_path}")




def merge_bliou_json_files(iob_data_path,BNER_data_path,jsonl_data_path,output_path = "data/all_entity_merged_THREE_data.json"):

    ob = IobToJSONbiluo()
    data1 = ob.convert_iob_to_biluo(file_path = iob_data_path)

    ob = IobToJSONbiluo()
    data2 = ob.convert_iob_to_biluo(file_path = BNER_data_path)

    obj = JsonlTobiluo()  
    data3 = obj.convert_jsonl_to_biluo_json_format(file_path = jsonl_data_path)

    merge_data = []
    id_cnt = 0
    for data in [data1,data2,data3]:
        for d in data:
            d['id'] = id_cnt
            id_cnt += 1
            merge_data.append(d)


    with open(output_path, 'w') as fp:
        json.dump(merge_data, fp, indent=2, ensure_ascii=False)
        print(f"Merge file save at: {output_path}")
    
    print("Total data samples:", id_cnt)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Merge BLIOU JSON files")
    parser.add_argument("iob_data_path", type=str, help="Path to the IOB data file")
    parser.add_argument("BNER_data_path", type=str, help="Path to the text data file")
    parser.add_argument("jsonl_data_path", type=str, help="Path to the JSONL data file")

    args = parser.parse_args()

    merge_bliou_json_files(args.iob_data_path,args.BNER_data_path, args.jsonl_data_path)
    

# python scripts/data_processing_all_entity.py data/all_data.txt data/main.jsonl





