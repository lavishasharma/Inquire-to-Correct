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
        self.instruction = args.question_prompt

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
