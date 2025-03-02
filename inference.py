import os
import json
import torch
import argparse 

from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        logging
)

from tqdm import tqdm

if __name__ == '__main__':
        def run():

                arguments = open("data/argument.txt").readlines()
                counter_arguments = open("data/counter-argument.txt").readlines()
                contexts = [eval(l)['qa_context'] for l in open('../generated_output/cmdr_ek_counter_argument.jsonl').readlines()]
                print("\tNumber of claims: " , len(arguments))
                print("\tNumber of counter-claims: " , len(counter_arguments))
                assert len(arguments) == len(counter_arguments), "The length of argument and counter-argument are different. Please check your data."
                output_file = open(args.output_file, 'w')
                
                for argument, context, counter_argument in tqdm(zip(arguments, contexts, counter_arguments), total=len(arguments)):

                        questions = get_questions(argument)

                        counter = get_counter_claim(argument, qacontext=context)
                        
                        output = {
                                'argument': argument, # input claim
                                'model': counter, # generated counter-claim 
                                'questions': questions, # generated questions from the input claim
                                'qa_context': context, # answers to the generated questions using web-search 
                                'counter-argument': counter_argument # "gold standard" counter-claim
                        }
                        json.dump(output, output_file, indent=4)

                return 

        def get_questions(claim: str):
                prompt = f'Generate 3 questions that will question the veracity of the given claim and persuade to take the opposing position: {claim}? Provide only querstions and nothing else. Questions: '
                model_input = tokenizer(prompt, return_tensors='pt').to('cuda')
                model_output = base_model.generate(**model_input, max_new_tokens=512, do_sample=True, top_k=50)
                result = tokenizer.decode(model_output[0], skip_special_tokens=True)
                result = result.split('Questions: ')[1]

                return result

        def get_counter_claim(claim: str, qacontext:str):
                if not qacontext:
                        prompt = f'Generate a succinct counter-argument that refutes the following claim: {claim}? Provide only the answer and nothing else. Do not give your opinion. Make sure the answer is no longer than 3 sentences. Counter-argument: '
                else:
                        prompt = f'Given the following context: {qacontext}, provide the counter-argument that refutes the following claim from the context: {claim}. Provide only the answer and nothing else. Do not give your opinion. Make sure the answer is no longer than 3 sentences. Counter-argument: '
                
                model_input = tokenizer(prompt, return_tensors='pt').to('cuda')
                model_output = base_model.generate(**model_input, max_new_tokens=512, do_sample=True, top_k=50)
                result = tokenizer.decode(model_output[0], skip_special_tokens=True)
                counter = result.split('Counter-argument: ')[1]

                return counter
        

        parser = argparse.ArgumentParser()
        parser.add_argument(
        "--model_name",
        type=str,
        required=True,
        help="Model from huggingface",
        )

        parser.add_argument(
        "--output_file",
        type=str,
        required=True,
        help="Path to save the generated data",
        )
        args = parser.parse_args()
        model_name = args.model_name
        base_model = AutoModelForCausalLM.from_pretrained(
        #base_model = AutoModelForSeq2SeqLM.from_pretrained(
                model_name,
                low_cpu_mem_usage=True,
                return_dict=True,
                torch_dtype=torch.float16,
                device_map='auto',
                )

                                     
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "right"

        logging.set_verbosity(logging.CRITICAL)
        run()

        
