import re
import tkinter as tk
import sys
import os
import customtkinter

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")


types=['double','int','float','char'] # data types of c programming language
reserved_wrods=['if','while','for','printf', 'scanf', 'main','else'] # key control words of c programming language
dic={'double':'0.0', 'int':'0','char':[],'float':'0.0'} # default values for each datatypes e.x if in c 'int c;'---> 'c .word 0' in mips
dic2={'int':'word','double':'double','char':'byte','float':'float'} # mapping of the data types of c and mips
numbers=re.compile(r"[0-9]") # using this for checking if a character is a number or not
  # keep track of the current line of the code
global line_number
line_number = 0
list_of_labels = ['main'] #holds list of labels
def compiler(input_expression):
    global  line_number
    line_number = 0
    mips_data=[]  # holds all program data 
    mips_text={'main:':[]} # holds all program text , first set the default label the text is in which is main label
    alphabet= re.compile(r"[a-z]",re.I) # using this for checking if a character is a alphabet letter or not 
    whitespace = re.compile(r"/s") # using this for checking if a character is a white space or not 
    curr=''  # first program text goes to main this will change when a control structures like if while or for are ecountered
    else_in_code = True in ['else' in int for int in input_expression] # checks if an else block exist in the code
    closed_brakets_number='' # for cases like c declaration 'char a[10];' which is translated as 'a .space 10'
    keyword='' # keep track if we ecountered if ,while or for keywords 
    check_numbers=False # indicate whether or not such 'char a[10]' has occured or not 
    variable_declaration=False #indicate whether or not the current expression is a variable declaration 
    string='' # holds the expression within the braket like while (a > b)
    buffer='' # holds the body of a block like while () {a = b+1;} implies buffer ='a = b+1;'
    start_block=False # indicate if we ecountered a start of if while or for body  
    expression_bool=False # indicate if we ecountered the expression of if while or for which is the bool expression within () these brackets

    dataType='' # keep track of the current data type


    for expression in input_expression:
        # if there are operators in the expression and they are not within the block of if for or while send the expression
        # and the current label for the program text to each respective fuction (if '+' to handle_add)
        # so the following if statements are for cases like 'a= b + 3' and the like with different operator and variables
        if '+' in expression and not '(' in expression and not start_block:
            handle_add(expression,curr,mips_data,mips_text)
            continue
        
        if '-' in expression and not '(' in expression and not start_block:
            handle_substraction(expression,curr,mips_data,mips_text)
            continue
        if '*' in expression and not '(' in expression and not start_block:
            handle_mult(expression,curr,mips_data,mips_text)
            continue
        if '/' in expression and not '(' in expression and not start_block:
            handle_division(expression,curr,mips_data,mips_text)
            continue
        if '%' in expression and not '(' in expression and not start_block:
            handle_modulo(expression,curr,mips_data,mips_text)
            continue
        current=0

        while current< len(expression):
            char=expression[current]
            if re.match(whitespace,char): # if char is a whitespace just skip it 
                current+=1
                continue
            if char=='{':# char is '{' indicate a start of a block set your start_block variable to True
                if keyword=='main':
                    string=''
                    curr='main:'
                else: 
                    start_block=True
                    current+=1
                    continue
            # if char is '}' indicate end of block so check your current keyword and call the appropraite fuction 
            # buffer and string holds the body and expression respectively
            if char=='}':
                
                if keyword=='if':
                    handle_if(string,buffer,curr,mips_data,mips_text,else_in_code)
                    curr='end:'
                if keyword=='while':
                    handle_while(string,buffer,curr,mips_data,mips_text)
                    curr='exit:'
                if keyword == 'for':
                    handle_for(string,buffer,curr,mips_data,mips_text)
                    curr='forExit:'
                if keyword == 'else':
                    handle_else(buffer,curr,mips_data,mips_text)
                current+=1
                keyword=''
                string=''
                buffer=''
                start_block=False

            if start_block:             
                buffer+=char  #holds the body of the block
                current+=1
                continue
            

            if char=='(':
                
                
                expression_bool=True
                current+=1
                continue
            if char==')':
                if keyword =='scanf': #if scanf key word is detected call the handle out put method
                    handle_input(string,curr,mips_data,mips_text)
                    keyword=''
                    string=''
                if keyword == 'printf': #if print key word is detected call the handle print method
                    handle_print(string,curr,mips_data,mips_text)
                    keyword=''
                    string=''
                expression_bool=False
                current+=1
                continue
            if expression_bool:
                string+=char  # string holds the the expression within the open bracket of the controls(if , while and for)
                current+=1
                continue

            if re.match(alphabet, char):
                # if char is a letter from a-z
                value = ''
                while re.match(alphabet, char):
                    value += char
                    current = current+1
                    char = expression[current]
                # know value holds a word 
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
                    
                
                    if variable_declaration: # if there is a variable declaration call the following fucntion
                        handle_declaration(expression,value,dataType,closed_brakets_number,mips_data,mips_text)

                        dataType=''
                        closed_brakets_number=''
                        variable_declaration=False
                        break
                        
                    if value in types: #if value is a data type then set your varible declaration to True and save the data type
                        
                        variable_declaration=True
                        dataType=value
                    
                    if value in reserved_wrods:
                        keyword=value  # if value is a control (if , while or for) or prinf or scanf save them for later


                        continue
            global list_of_labels
            if list_of_labels[-1] != curr:
                list_of_labels.append(curr)
            current+=1
        # global line_number
        line_number+=1




    return mips_text,mips_data
        
            

# handle cases like 'int a=4 ;' or 'int a;' without any value or even 'char a "b"' or 'char a[10]'

def handle_declaration(expression,name,dataType,numbers,mips_data,mips_text):
    expression=expression.strip() 
    if '=' in expression: # if name is provided in the declaration

        declartion = expression.split('=')
        if numbers or '[' in expression:
            mips_data.append(name + ":  " + '.' + "asciiz" + " " + remove_colon(declartion[1]))




        else:


            mips_data.append(name + ":  " + '.'+ dic2[dataType] + " " + remove_colon(declartion[1]))
        
        
    else: # if value is not provided or it is case like 'char a "b"'
        declartion=expression.split(' ')

        if numbers: # if there is a number wuthin the square brackets[] like 'char a[10]' ---> 'a: .space 10' in mips
            mips_data.append(declartion[1][:declartion[1].index('[')] + ': ' + '.space ' + numbers)

        else:
            # if it is like 'char a "b"' ---> 'a: .byte "b" ' in mips #remove_colon(declartion[-1])
            if dataType=='char':
                mips_data.append(name + ":  " +  '.'  + dic2[dataType] )
            # if it is like 'int a;' use default values ---> 'a: .word 0'
            else:
                mips_data.append(name + ":  " +  '.'  + dic2[dataType] + " " +dic[declartion[0]])
            
# takes two operands and the current label and an idication for wether it is from the expression of controls(if, while or for)
#
def handle_operand(operands1, operands2,label,mips_data,mips_text):
    operands2=operands2.strip() # can be a variable or an immediate  e.x a or 4 
    operands1=operands1.strip()  # can be a variable or an immediate
    if not operands1.isnumeric(): # if it is a variable 
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
        
        # know type_ is word or float or byte or any kind of mips data type
        if type_=='word':
          
            mips_text[label].append('lw $t0 ,' + remove_colon(operands1))
        

        if type_=='float' or type_=='double':
            mips_text[label].append('lwc1 $f0 ,' + remove_colon(operands1))

    else:
        mips_text[label].append('li $t0 ,' + remove_colon(operands1))
        type_='word'

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
            mips_text[label].append('lw $t1 ,' + remove_colon(operands2))

        if type_=='float' or type_=='double' :
            mips_text[label].append('lwc1 $f2 ,' + remove_colon(operands2))

    else:
    
        mips_text[label].append('li $t1 ,' + remove_colon(operands2))
        type_='word'
    return type_

def handle_if(expression, body,curr,mips_data,mips_text,else_in_code):
    body=body.split(';')
    label='condition:'
    
    
    mips_text['condition:']=[]
    
    operators=['==', '!=','>=',"<=",'<','>']
    dic_map={'<':'blt','>':'bgt','==':'beq','!=':'!=bne','>=':'bge','<=':'ble'}

    for ope in operators:
        if ope in expression:
            expression=expression.split(ope)
            type_=handle_operand(expression[0],expression[1],curr,mips_data,mips_text)
            
            if type_=='word':
                mips_text[curr].append(dic_map[ope] + ' $t0, ' + '$t1, ' + 'condition' )

                if else_in_code:
                    pass
                else:
                    mips_text[curr].append('j end')
            break
    handle_body(body,label,mips_data,mips_text)
    mips_text['end:']=[]
def handle_else(body,curr,mips_data,mips_text):
    if len(list_of_labels) == 1:
        label = 'main'
    else:
        label = list_of_labels[-2]

    body = body.split(';')
    handle_body(body,label , mips_data, mips_text)
    mips_text[label].append('j end')

def handle_while(expression, body,curr,mips_data,mips_text):
    expression=expression.strip()
    body=body.split(';')
    label='while:'
    mips_text['while:']=[]
    
    operators=['==', '!=','>=',"<=",'<','>']
    dic_map={'<':'bge','>':'ble','==':'bne','!=':'!=beq','>=':'blt','<=':'bgt'}

    for ope in operators:
        if ope in expression:
            expression=expression.split(ope)
            type_=handle_operand(expression[0],expression[1],label,mips_data,mips_text)
            if type_=='word':
                mips_text[label].append(dic_map[ope] + ' $t0, ' + '$t1, ' + 'exit' )
                
            break
    handle_body(body,label,mips_data,mips_text)

    mips_text[label].append('j while')
    mips_text['exit:'] = []
def handle_for(expression, body,curr,mips_data,mips_text):
    expression=expression.split(';') # example expression = "i=0; i<=5; ++i"
    body=body.split(';')
    operators=['==', '!=','>=',"<=",'<','>']
    dic_map={'<':'bge','>':'ble','==':'bne','!=':'!=beq','>=':'blt','<=':'bgt'}
    statement1=expression[0].strip() # i=0
    handle_assignment(statement1,curr,mips_data,mips_text) # handles assignment like i=0
    label='for:'
    mips_text['for:']=[]

    statement2=expression[1].strip()
    for ope in operators:
        if ope in statement2:
            statement2=statement2.split(ope)
            type_=handle_operand(statement2[0],statement2[1],label,mips_data,mips_text)
            if type_=='word':
                mips_text[label].append(dic_map[ope] + ' $t0, ' + '$t1, ' + 'forExit' )
                
            break
    statement3 =expression[2].strip()
    var=''
    for char in statement3:
        if char!='-' and char!='+':
            var+=char

    if '++' in statement3:
        mips_text[label].append('addi $t0 , $t0, 1')
        mips_text[label].append('sw $t0, ' + var)
    if '--' in statement3:
        mips_text[label].append('subi $t0, $t0, 1')
        mips_text[label].append('sw $t0, ' + var)
    handle_body(body,label,mips_data,mips_text)
    mips_text[label].append('j for')
    mips_text['forExit:']=[]

def handle_assignment(statement,curr,mips_data,mips_text):
    statement=statement.split('=')
    type_=handle_operand(statement[0],statement[1],curr,mips_data,mips_text)
    if type_=='word':
        mips_text[curr].append('add $t0, $t1, $zero')
        mips_text[curr].append('sw $t0, ' + statement[0])


def handle_body(body, label,mips_data,mips_text):
    body = [element.strip() for element in body]

    for statement in body:
        if '+' in statement:
            handle_add(statement, label ,mips_data,mips_text)
        if '-' in statement:
            handle_substraction(statement, label,mips_data,mips_text)
        if '*' in statement:
            handle_mult(statement, label,mips_data,mips_text)
        if '/' in statement:
            handle_division(statement, label,mips_data,mips_text)
        if '%' in statement:
            if '(' not in statement:
                handle_modulo(statement, label,mips_data,mips_text)
        if '(' in statement:
            alphabet = re.compile(r"[a-z]", re.I)
            current = 0
            string = ''
            keyword = ''
            expression_bool = False
            while current < len(statement):
                char = statement[current]
                if char == ' ':
                    current += 1
                    continue
                if char == '(':
                    expression_bool = True
                    current += 1
                    continue
                if char == ')':
                    if keyword == 'scanf':  # if scanf key word is detected call the handle out put method
                        handle_input(string, label,mips_data,mips_text)
                        keyword = ''
                        string = ''
                    if keyword == 'printf':  # if print key word is detected call the handle print method
                        handle_print(string, label,mips_data,mips_text)
                        keyword = ''
                        string = ''
                    expression_bool = False
                    current += 1
                    continue
                if expression_bool:
                    string += char  # string holds the the expression within the open bracket of the controls(if , while and for)
                    current += 1
                    continue

                if re.match(alphabet, char):
                    value = ''
                    while re.match(alphabet, char):
                        value += char
                        current = current + 1
                        char = statement[current]
                if value in reserved_wrods:
                    keyword = value  # if value is a control (if , while or for) or prinf or scanf save them for later
                    continue
                current += 1


    
def handle_add(expression,label,mips_data,mips_text):
    lst=expression.split('=')
    operands=lst[1].split('+')
    type_=handle_operand(operands[0],operands[1],label,mips_data,mips_text)

        
    if type_ =='word':
        mips_text[label].append('add $t2, $t1, $t0'  )
        mips_text[label].append('sw $t2, ' +lst[0])
    if type_ == 'float':
        mips_text[label].append('add.s $f4, $f2, $f0')
        mips_text[label].append('s.s $f4, ' +  lst[0])
    if type_=='double':
        mips_text[label].append('add.d $f4, $f2, $f0')
        mips_text[label].append('s.d $f4, ' + lst[0])


def handle_substraction(expression,label,mips_data,mips_text):
    lst=expression.split('=')
    operands=lst[1].split('-')
    type_=handle_operand(operands[0],operands[1],label,mips_data,mips_text)

    if type_ =='word':
        mips_text[label].append('sub $t2, $t0, $t1'  )
        mips_text[label].append('sw $t2, ' +lst[0])
    if type_ == 'float':
        mips_text[label].append('sub.s $f4, $f0, $f2')
        mips_text[label].append('s.s $f4, ' +  lst[0])
    if type_=='double':
        mips_text[label].append('sub.d $f4, $f0, $f2')
        mips_text[label].append('s.d $f4, ' + lst[0])

def handle_mult(expression,label,mips_data,mips_text):
    lst=expression.split('=')
    operands=lst[1].split('*')
    type_=handle_operand(operands[0],operands[1],label,mips_data,mips_text)

    if type_ =='word':
        mips_text[label].append('mul $t2, $t1, $t0'  )
        mips_text[label].append('sw $t2, ' +lst[0])
    if type_ == 'float':
        mips_text[label].append('mul.s $f4, $f2, $f0')
        mips_text[label].append('s.s $f4, ' +  lst[0])
    if type_=='double':
        mips_text[label].append('mul.d $f4, $f2, $f0')
        mips_text[label].append('s.d $f4, ' + lst[0])
def handle_division(expression,label,mips_data,mips_text):
    lst=expression.split('=')
    operands=lst[1].split('/')
    type_=handle_operand(operands[0],operands[1],label,mips_data,mips_text)

    if type_ =='word':
        mips_text[label].append('div $t2, $t0, $t1'  )
        mips_text[label].append('sw $t2, ' +lst[0])
    if type_ == 'float':
        mips_text[label].append('div.s $f4, $f0, $f2')
        mips_text[label].append('s.s $f4, ' +  lst[0])
    if type_=='double':
        mips_text[label].append('div.d $f4, $f0, $2')
        mips_text[label].append('s.d $f4, ' + lst[0])
def handle_modulo(expression,label,mips_data,mips_text):
    lst=expression.split('=')
    operands=lst[1].split('%')

    type_=handle_operand(operands[0],operands[1],label,mips_data,mips_text)

   
    mips_text[label].append('div $t0, $t1'  )
    mips_text[label].append('mfhi $t2')

    mips_text[label].append('sw $t2,' +lst[0])


def remove_colon(word):
    lst=list(word)
    if ';' in lst:
        lst.pop()
    return ''.join(lst)
def handle_print(body, label,mips_data,mips_text):
    # The body contains plain text in there is no % sign
    # prinf('enter a number')

    if '%' not in body:
        # store the text in a temporary variable
        mips_data.append(f'temp{line_number}: .asciiz {body}')
        mips_text[label].append(f'li $v0, 4')
        mips_text[label].append(f'la $a0, temp{line_number}')
        mips_text[label].append(f'syscall')


    else:
        body = body.split(',')
        message = body[0]
        variable = body[1]

        #  printf("%d", variable);
        if 'd' in message:
            mips_text[label].append(f'li $v0, 1')
            mips_text[label].append(f'lw $a0, {variable.strip()}')
            mips_text[label].append(f'syscall')

        #  printf("%f", variable);
        if 'f' in message and not '1' in message:
            mips_text[label].append(f'li $v0, 2')
            mips_text[label].append(f'lwc1 $f12, {variable.strip()}')
            mips_text[label].append(f'syscall')

        #  printf("%1f", variable);
        if '1f' in message:
            mips_text[label].append(f'li $v0, 3')
            mips_text[label].append(f'ldc1 $f12, {variable.strip()}')
            mips_text[label].append(f'syscall')
            
            
        #  printf("%c", variable);
        if 'c' in message:
            mips_text[label].append(f'li $v0, 11')
            mips_text[label].append(f'lb $a0, {variable.strip()}')
            mips_text[label].append(f'syscall')
        if 's' in message:
            mips_text[label].append(f'li $v0, 4')
            mips_text[label].append(f'la $a0, {variable.strip()}')
            mips_text[label].append(f'syscall')



#  scanf("%d%f%1f%c%s", &a, &b,&c,$d,$string);
#scanf()
def handle_input(body,label,mips_data,mips_text): # handles input statement

    #mips i/0 li $v0,5 for integer
    #li $v0,6 for float
    # li $v0,7 double
    # li $v0,8 string



    body = body.split(',')

    input_type = body[0] # extract the format string leaving the variables in the body
    body.remove(input_type)
    input_type = list(input_type)
    input_type.pop()
    input_type.pop(0)

    input_type = ''.join(input_type)

    input_type = input_type.split('%')
    input_type.pop(0)

    for i in range(len(input_type)):
    # iterate through the different input types to prepare input statement for each type in mips
        variable = body[i]
        variable = variable.strip()
        variable = variable[1:]





        if input_type[i] == 'd': # for integer
            mips_text[label].append('li $v0, 5')
            mips_text[label].append('syscall')
            mips_text[label].append(f'sw $v0 ,{variable}')
            continue

        if input_type[i]== 'f': # for float
            mips_text[label].append('li $v0 6')
            mips_text[label].append('syscall')
            mips_text[label].append(f'swc1 $f0, {variable}')
            continue


        if input_type[i]== '1f': #for double
            mips_text[label].append('li $v0 7')
            mips_text[label].append('syscall')
            mips_text[label].append(f'sdc1 $f0, {variable}')
            continue

        if input_type[i]== 'c': #for character
            mips_text[label].append('li $v0 12')
            mips_text[label].append('syscall')
            mips_text[label].append(f'sb $v0, {variable}')
            continue
        if input_type[i]== 's': #for string


            string_size = ''
            string_name = ''
            for data in mips_data:
                # This loop is used to locate the variable
                # declaration and extract the size of the input string
                string_name = body[i][1:]

                if string_name in data:
                    index = data.find('.')
                    index = index + 6
                    string_size = data[index:].strip()
                    break

            mips_text[label].append(f'li $v0, 8')
            mips_text[label].append(f'la $a0, {string_name} ')
            mips_text[label].append(f'li $a1, {string_size} ')
            mips_text[label].append(f'syscall')
#  scanf("%d%f", &a, &b);
    

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
def run(source):

    expression_=removeComments(source.splitlines())
    mips_text,mips_data=compiler(expression_)
    tab='\t'
    print('.data')
    for data in mips_data:
        print(tab,data)

    print('.text')
    for text in mips_text.keys():
        print(text)
        for instruction in mips_text[text]:
            print(tab,instruction)
        
    print(tab,'li $v0,10')
    print(tab ,'syscall')
    








class GUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
       
        toolbar = tk.Frame(self)
        
      
        
        toolbar.columnconfigure(0, weight = 1)
        toolbar.columnconfigure(1, weight = 1)
        
        label = tk.Label(self, text="C TO ASSEMBLY COMPILER", font=(18))
        label.grid(row = 0, column = 0)
        
        
        b1 =  customtkinter.CTkButton(self, text="COMPILE", command=self.print_stdout)
        b2 = customtkinter.CTkButton(self, text="RESET",  command=self.clear_text)
        b1.grid(row= 1, column = 1, sticky=tk.W+tk.E)
        b2.grid(row= 2, column = 1, sticky=tk.W+tk.E)
        self.text1 = customtkinter.CTkTextbox(self, width=1250,font=("arial", 18), height=370)
        font = customtkinter.CTkFont(size=18)
       
        self.text1.grid(row= 1, column = 0, sticky=tk.W+tk.E, pady =10,padx=10)
        self.text = customtkinter.CTkTextbox(self, width=1000,font=("arial", 18), height=370)
       
        self.text.grid(row = 2, column = 0, sticky=tk.W+tk.E, pady =10, padx=10)
        
        

        sys.stdout = TextRedirector(self.text, "stdout")
        sys.stderr = TextRedirector(self.text, "stderr")
        
   

    def print_stdout(self):
            source  = self.text1.get('1.0', tk.END)
            run(source)
        

    
    def clear_text(self):
            self.text.delete('1.0', tk.END)



            


class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.configure(state="normal")
        self.widget.insert("end", str, (self.tag,))
        
        

app = GUI()
app.mainloop()










