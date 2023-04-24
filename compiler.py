import re

mips_data=[]
mips_text={'main':[]}
types=['double','int','float','char']
reserved_wrods=['if']
dic={'double':'0.0', 'int':'0','char':[],'float':'0.0'}
dic2={'int':'word','double':'double','char':'byte','float':'float'}
numbers=re.compile(r"[0-9]")

def compiler(input_expression):
    alphabet= re.compile(r"[a-z]",re.I)
    whitespace = re.compile(r"/s")

    closed_brakets_number=''
    keyword=''
    check_numbers=False
    variable_declaration=False
    string=''
    buffer=''
    start_block=False
    expression_bool=False
    

    dataType='' 
    for expression in input_expression:
        if '+' in expression and not '(' in expression and not start_block:
            handle_add(expression,'main')
            continue
        if '-' in expression and not '(' in expression and not start_block:
            handle_substraction(expression,'main')
            continue
        if '*' in expression and not '(' in expression and not start_block:
            handle_mult(expression,'main')
            continue
        if '/' in expression and not '(' in expression and not start_block:
            handle_division(expression,'main')
            continue
        if '%' in expression and not '(' in expression and not start_block:
            handle_modulo(expression,'main')
            continue
        current=0
        while current< len(expression):
            char=expression[current]
            if re.match(whitespace,char):
                current+=1
                continue
            if char=='{':
                start_block=True
                current+=1
                continue
            if char=='}':
                if keyword=='if':
                    handle_if(string,buffer)
                current+=1
                keyword=''
                start_block=False
            if start_block:             
                buffer+=char
                current+=1
                continue
            

            if char=='(':
                expression_bool=True
                current+=1
                continue
            if char==')':
                expression_bool=False
                current+=1
                continue
            if expression_bool:
                string+=char
                current+=1
                continue

            if re.match(alphabet, char):
                value = ''
                while re.match(alphabet, char):
                    value += char
                    current = current+1
                    char = expression[current]
                if not start_block:
                    if char=='[' and variable_declaration:
                        check_numbers=True
                        current+=1
                    char = expression[current]   
                    if char==']':
                        check_numbers=False
                        current+=1
                    char = expression[current]
                    if check_numbers:
                        num = ''
                        while re.match(numbers, char):
                            num += char
                            current = current+1
                            char = expression[current]
                    
                        closed_brakets_number=num
                    
                
                    if variable_declaration:
                        handle_declaration(expression,value,dataType,closed_brakets_number)

                        dataType=''
                        closed_brakets_number=''
                        variable_declaration=False
                        break
                            

                    
                    if value in types:
                        
                        variable_declaration=True
                        dataType=value
                    
                    if value in reserved_wrods:
                        keyword=value   
            current+=1

def handle_declaration(expression,value,dataType,numbers):

    if '=' in expression:
        declartion=expression.split('=')
        mips_data.append(value + ":  " + '.'+ dic2[dataType] + " " + remove_colon(declartion[1]))
        
        
    else:
        declartion=expression.split(' ')
        if numbers:
            mips_data.append(declartion[1][:declartion[1].index('[')] + ': ' + '.space ' + numbers)

        else:
            
            if dataType=='char':
                mips_data.append(value + ":  " +  '.'  + dic2[dataType] + " " + remove_colon(declartion[-1])) 
            else:
                mips_data.append(value + ":  " +  '.'  + dic2[dataType] + " " +dic[declartion[0]])

def handle_operand(operands1, operands2,label):
    operands2=operands2.strip()
    operands1=operands1.strip()
    
    if not operands1.isnumeric():
        for data in mips_data:
            if operands1 in data:
                saved=data
                break
        i=saved.index('.')
        i+=1
        type_=''
        while i< len(saved):
            if saved[i]==' ':
                break
            type_+=saved[i] 
            i+=1
        if type_=='word':
            mips_text[label].append('lw $t0 ,' + operands1)
        if type_=='float' or type_=='double':
            mips_text[label].append('lwc1 $f0 ,' + operands1)

    else:
        mips_text[label].append('li $t0 ,' + operands1)

    if not operands2.isnumeric():
        for data in mips_data:
            if operands2 in data:
                saved=data
                break
        i=saved.index('.')
        i+=1
        type_=''
        while i< len(saved):
            if saved[i]==' ':
                break
            type_+=saved[i] 
            i+=1
        if type_=='word':
            mips_text[label].append('lw $t1 ,' + operands2)
        if type_=='float' or type_=='double' :
            mips_text[label].append('lwc1 $f2 ,' + operands2)

    else:
        mips_text[label].append('li $t1 ,' + operands2)
    return type_

def handle_if(expression, body):
    body=body.split(';')
    label='condition'
    mips_text['condition']=[]
    operatots=['==', '!=','>=',"<=",'<','>']
    dic_map={'<':'blt','>':'bgt','==':'beq','!=':'!=bne','>=':'bge','<=':'ble'}

    for ope in operatots:
        if ope in expression:
            expression=expression.split(ope)
            type_=handle_operand(expression[0],expression[1],'main')
            if type_=='word':
                mips_text['main'].append(dic_map[ope] + ' $t0, ' + '$t1, ' + 'condition' )
            break
    for statement in body:
        if '+' in statement:
            handle_add(statement,label)
        if '-' in statement:
            handle_substraction(statement,label)
        if '*' in statement:
            handle_mult(statement,label)
        if '/' in statement:
            handle_division(statement,label)
        if '%' in statement:
            handle_modulo(statement,label)
    

    
def handle_add(expression,label):
    lst=expression.split('=')
    operands=lst[1].split('+')
    type_=handle_operand(operands[0],operands[1],label)

        
    if type_ =='word':
        mips_text[label].append('add $t2, $t1, $t0'  )
        mips_text[label].append('sw $t2, ' +lst[0])
    if type_ == 'float':
        mips_text[label].append('add.s $f4, $f2, $f0')
        mips_text[label].append('s.s $f4, ' +  lst[0])
    if type_=='double':
        mips_text[label].append('add.d $f4, $f2, $f0')
        mips_text[label].append('s.d $f4, ' + lst[0])


def handle_substraction(expression,label):
    lst=expression.split('=')
    operands=lst[1].split('-')
    type_=handle_operand(operands[0],operands[1],label)

    if type_ =='word':
        mips_text[label].append('sub $t2, $t1, $t0'  )
        mips_text[label].append('sw $t2, ' +lst[0])
    if type_ == 'float':
        mips_text[label].append('sub.s $f4, $f2, $f0')
        mips_text[label].append('s.s $f4, ' +  lst[0])
    if type_=='double':
        mips_text[label].append('sub.d $f4, $f2, $f0')
        mips_text[label].append('s.d $f4, ' + lst[0])

def handle_mult(expression,label):
    lst=expression.split('=')
    operands=lst[1].split('*')
    type_=handle_operand(operands[0],operands[1],label)

    if type_ =='word':
        mips_text[label].append('mul $t2, $t1, $t0'  )
        mips_text[label].append('sw $t2, ' +lst[0])
    if type_ == 'float':
        mips_text[label].append('mul.s $f4, $f2, $f0')
        mips_text[label].append('s.s $f4, ' +  lst[0])
    if type_=='double':
        mips_text[label].append('mul.d $f4, $f2, $f0')
        mips_text[label].append('s.d $f4, ' + lst[0])
def handle_division(expression,label):
    lst=expression.split('=')
    operands=lst[1].split('/')
    type_=handle_operand(operands[0],operands[1],label)

    if type_ =='word':
        mips_text[label].append('div $t2, $t1, $t0'  )
        mips_text[label].append('sw $t2, ' +lst[0])
    if type_ == 'float':
        mips_text[label].append('div.s $f4, $f2, $f0')
        mips_text[label].append('s.s $f4, ' +  lst[0])
    if type_=='double':
        mips_text[label].append('div.d $f4, $f2, $f0')
        mips_text[label].append('s.d $f4, ' + lst[0])
def handle_modulo(expression,label):
    lst=expression.split('=')
    operands=lst[1].split('%')

    type_=handle_operand(operands[0],operands[1],label)

   
    mips_text[label].append('div $t1, $t0'  )
    mips_text[label].append('mfhi $t2')

    mips_text[label].append('sw $t2,' +lst[0])


def remove_colon(word):
    lst=list(word)
    lst.pop()
    return ''.join(lst)
                    
compiler(["int a = 3 ;","int b = 4;", 'int c;',"char chr[8];"," if (a>= b ){","c=a%b;}"])
for data in mips_data:
    print(data)
print(mips_text)
tab='\t'
for text in mips_text.keys():
    print(text)
    for instruction in mips_text[text]:
        print(tab,instruction)
    print('li $v0,10')
    print('syscall')
source='''
#include<stdio.h>
int main() {
  double first;
  double second;
  double  temp;
  printf("Enter first number: ");
  scanf("%lf", &first);
  printf("Enter second number: ");
  scanf("%lf", &second);

  // value of first is assigned to temp
  temp = first;

  // value of second is assigned to first
  first = second;

  // value of temp (initial value of first) is assigned to second
  second = temp;

  // %.2lf displays number up to 2 decimal points
  printf("\nAfter swapping, first number = %.2lf\n", first);
  printf("After swapping, second number = %.2lf", second);
  return 0;
}'''      

def removeComments(source):
        result=[]
        start_comment=False #signal if we are have found our block comment starting point 
        buffer=''
           
        for item in source:
            start=0  
            while start<len(item):
               

                if start< len(item)-1 and item[start]=="/" and item[start+1]=='/' and not start_comment:
                    start=len(item)
                    
                elif start< len(item)-1 and item[start]=="/" and item[start+1]=='*' and not start_comment:
                    start_comment=True 
                    start+=1
                elif start< len(item)-1 and item[start]=="*" and item[start+1]=='/' and start_comment:
                    start_comment=False
                    start+=1
                elif not start_comment:
                    buffer+=item[start]
                start+=1
            if buffer and not start_comment:
                result.append(buffer)
                buffer=''
        return result
# expression=removeComments(source.splitlines())
# print(expression)
"""

.data

.text

     main:
         bgt $t0,$t1 , condition 
         lw 
         li $v0,10
         syscall 
    condition:
          addi $t2,2,3


"""






