from vllm import LLM, SamplingParams

class QuestionGenerator:
    def __init__(self, args):
        self.args = args
        self.llm = LLM(model=self.args.model_name)
        self.sampling_params = SamplingParams(
            temperature=args.temperature,
            seed=args.seed,
            max_tokens=100,
            stop=["]"],
            include_stop_str_in_output=True
        )
        self.instruction = """As a question generator, your task is to produce a variety of questions (extractive and abstractive) for a given answer and context. Given an answer and a context as input, your goal is to generate abstractive, extractive, and yes/no questions from the context sentence, such that the answer to these questions is the word or phrase given as input. Please provide at least one question for each type of question (abstractive, extractive, yes/no) and enclose each question in double quotations.
Generate atleast 5 questions.

For example:

Input:
Context: John's cat weighs 30 pounds.
Answer: 'John's cat'
Output: ["Whose cat weighs 30 pounds?", "What weighs 30 pounds?", "What does John have that weighs 30 pounds?", "Which pet of whose pet weighs 30 pounds?", "Which pet of John's weighs 30 pounds?"]"""

    def generate(self, samples: list):
        o_id={}
        prompt_dict={}
        j=0
        import ast
        for key in range(len(samples)):
            i=samples[key]['input_claim']
            try:
                list_of_answers=ast.literal_eval(samples[key]['entities'])
            except:
                list_of_answers=samples[key]['entities'].replace("[","").replace("]","").split("', '")
                #print(list_of_answers)
                #break
            prompt_qg=self.instruction+"""\n\nInput:\nContext:\" """+i+"""\"\nAnswer: '"""
            prompt_answer=""

            for answer in list_of_answers:
                prompt_answer=prompt_qg+answer+"'"+"\n"
                prompt_dict[j]=prompt_answer
                o_id[j]=key
                j=j+1        
        prompt_list=list(prompt_dict.values())
        outputs = self.llm.generate(prompt_list, self.sampling_params)
        import ast
        s=dict(zip(list(prompt_dict.keys()),outputs))
        for i in s:
          generated=s[i].outputs[0].text
          #print(generated)

          try:
              f=generated.split("Output:")[1]
              if "]" not in generated:
                  f=f+']'
                  f=f.strip(' ')

              s[i]=ast.literal_eval(f)
              #print(".")
          except:
              try:
                  l=f.split("]")[0]+']'
                  if "[" not in l:
                        l="["+l
                  s[i]=ast.literal_eval(l)
                  #print("..")
              except:
                  l1=l.strip("]")
                  iind=l1.index("[")+1
                  m=l1[iind:]
                  try:
                    s[i]=m.split('", "')
                  except:
                    try:
                        s[i]=m.split('", "')
                    except:
                        s[i]=m.split(',')
          for e in range(0,len(s[i])):
            s[i][e]=s[i][e].strip("\"")  

        for i in range(len(samples)):
            samples[i]["questions"]=[]

        for i in s:
            try:
                samples[o_id[i]]["questions"].extend(s[i])

            except:
                samples[o_id[i]]["questions"]=str(samples[o_id[i]]["questions"])+s[i]
        for i in range(len(samples)):
            try:
                samples[i]['questions']=list(set(samples[i]['questions']))
            except:
                pass
        return samples
