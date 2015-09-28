# -*- coding: utf-8 -*-
"""
Tex2SPIP

Translate Latex file to Spip text ready for copy/paste
In case of tikz or other stuff impossible to compile for spip latex server,
the script generates pictures to be imported in spip

@author: Steven Masfaraud (steven@masfaraud.fr)
"""

import sys
import os

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return None

def find_between_r( s, first, last ):
    """
    Recursive version?
    """
    try:
        start = s.rindex( first ) + len( first )
        end = s.rindex( last, start )
        return s[start:end]
    except ValueError:
        return None

#def find_latex_tag(string,tag):# Opening  of tag
#    if '\\'+tag+'{' in string:
#        return string.index('\\'+tag+'{')
#    else:
#        return False

#def find_latex_opening_tag(string,tag):
#    return find_between_r(string,'\\'+tag+'{','}')
#
#def find_latex_closing_tag(string,tag):
#    return find_between_r(string,'\\'+tag+'{','}')


#def find_latex_env(string,env):
#    return find_between_r(string,'\begin{'+env+'}','\end{'+env+'}')
#
#def detect_latex_begin_env(string,env):
#    return '\begin{'+env+'}' in string
#
#def detect_latex_end_env(string,env):
#    return '\end{'+env+'}' in string

#def detect_latex_tag(string):
    
n=len(sys.argv)
#print n
#print sys.argv[0]
if n>2:
    input_file=sys.argv[1]
    output_file=sys.argv[2]
elif n==2:
    input_file=sys.argv[1]
    output_file='output.spip'
else:
    print 'Error: no latex file given'


#tags=['section','subsection','subsubsection']
#envs=['equation','itemize']

def ReadFile(input_file,output='string'):
    if output=='list':     
        code=[]
    else:
        code=''
    with open(input_file, "r") as code_file:
            line=code_file.readline()
            while line!='':
                if output=='list':
                    code.append(line)                
                else:
                    code+=line
                line=code_file.readline()# Line update
    return code

def WriteFile(code,output_file):
    with open(output_file,"w") as code_file:
        if type(code)==list:
            for line in code:
                code_file.write(line)
        else:
            code_file.write(code)
            
#def ParenthethisAnalysis(string,pb=0):
##    po=0
##    pb=0
##    pb-=(string.count('{')-string.count('}'))
#    indices=[i for i,x in enumerate(line) if (x=='}')|(x=='{')]
#    for ind in indices:
#        if line[ind]=='{':
#            pb+=1
#        elif line[ind]=='}':
#            pb-=1
#        if pb==0:
#            return (True,ind)
#        else:
#            return (False,pb)
    

class L2STranslator:
    def __init__(self,input_file,output_file):
        self.input_file=input_file
        self.output_file=output_file
        self.latex_code=ReadFile(input_file,output='string')+'\n'
#        self.current_line=0
        self.current_column=0
        self.image_number=1
        self.current_language=''
        

        self.current_directory=os.path.dirname(os.path.abspath(input_file))# Usefull to have absolute path for inputs
        if (not self.current_directory=='')&(not self.current_directory[-1]=='/'):
            self.current_directory+='/'
#    def TranslateItemize(self,code_input):
#        code_input.replace('\item','-*',)
        
        
    def DeleteComments(self):

        comments=[]        
        comment='aa'
        code=self.latex_code
        while comment!=None:
            comment=find_between(code,'%','\n')
            comments.append(comment)
            if comment!=None:
                code=code.replace('%'+comment,'')
        for comment in comments:
            if comment!=None:
                if not '\%'+comment+'\n' in self.latex_code:# Si le % n'est pas échappé:
#                    print self.latex_code.replace('%'+comment,'')
                    self.latex_code=self.latex_code.replace('%'+comment+'\n','\n')
   
    def FindLatexEnv(self,string,env):# Opening  of tag
        if '\\begin{'+env+'}' in string:
            return string.index('\\begin{'+env+'}')
        else:
            return None
            
    def AnalyseTabular(self,string):
        """ return list rows containig list of elements
            by analysing string (tabular content or eqnarray or whatever)
        """
        cells=[]
        cells2=[]
#        print string
#        string=string.replace('\n','\\\\')
        while len(string)!=0:
            end=string.find('\\\\')
            if end>0:
                cells.append(string[0:end])
            string=string[end+2:]
        for cell in cells:
            cell+='&'# Trick to avoid conditionnal programming
            cell=cell.replace('\n','')
            cell2=[]
            while len(cell)!=0:
                end=cell.find('&')
                cell2.append(cell[0:end])
                cell=cell[end+1:]
            cells2.append(cell2)            
            
        return cells2
            
            
    def FindEnvContent(self,ind):
        env=self.FindTagArgs(ind)
        env=env[0]
        
        ind=0
        l=len(self.latex_code)
#        print l
        i1=l
        i2=i1
        bb=0
        niter=0
        remaining_code=self.latex_code
        
        while ind<l:
            remaining_code=remaining_code[ind:]
            l=len(remaining_code)
            if '\\begin{'+env+'}' in remaining_code:
                i1=remaining_code.index('\\begin{'+env+'}')+8+len(env)
            else:
                i1=l
            if '\end{'+env+'}' in remaining_code:
                i2=remaining_code.index('\end{'+env+'}')+6+len(env)
            else:
                i2=l
            if i1<i2:
                bb+=1
                ind=i1
                if bb==1:
                    begin_env=ind
            else:
                bb-=1
                ind=i2
                if bb==0:
                    end_env=ind+self.latex_code.index(remaining_code)-6-len(env)#
                    ind=l
            niter+=1
#            print niter
            if niter>26:
                break
#        print 'content: ',self.latex_code[begin_env:end_env]
        return self.latex_code[begin_env:end_env]
            
             
    def FindLatexTag(self,string,tag):# Opening  of tag
        if '\\'+tag+'{' in string:
            return string.index('\\'+tag+'{')
        else:
            return None
            
    def FindTagArgs(self,ind):
        if not type(ind)==int:
            print 'index must be int'
            return None
        # finding args of tag begining at ind
        args=[]
        pb=0
        cp=0

        l=len(self.latex_code)
#        print l
        while ind<=l-1:
#            print ind,l-1
#            print self.latex_code[ind]
#            os.system("""bash -c 'read -s -n 1 -p "Press any key to continue...\n"'""")
            if self.latex_code[ind]=='{':
                pb+=1
                if pb==1:
                    begin_arg=ind+1
#                print 'pb: ',pb
            elif self.latex_code[ind]=='}':
                pb-=1
                if pb==0:
                    cp+=1
#                print 'pb: ',pb
#                print 'cp: ',cp
#                print (pb==0)&(cp!=0)

                if (pb==0)&(cp!=0):# Closed parenthethis
                    #store as argument
#                    print 'store'
                    args.append(self.latex_code[begin_arg:ind])
                    # If next non empty string string is an open parenthethis -> new arg -> don't break
#                    print self.latex_code[ind]
                    i=1
                    while ((self.latex_code[ind+i]=='\n')|(self.latex_code[ind+i]==' '))&((ind+i)!=l-1):
                        i+=1
#                        print ind+i,'/',l-1
#                        print self.latex_code[ind+i]
#                    print self.latex_code[ind+i]
                    if (ind+i)!=l-1:
                        if not self.latex_code[ind+i]=='{':
                            break
            ind+=1
#            os.system("""bash -c 'read -s -n 1 -p "Press any key to continue...\n"'""")
        return args

    def Translate(self):
        
        # Delete \\ when at end of line, replace with \n if inside a line
#        self.latex_code=self.latex_code.replace('\\\n','\n')
#        self.latex_code=self.latex_code.replace('\\\n','\n')
#        self.latex_code=self.latex_code.replace('\\\n','\n')
        self.DeleteComments()
        # Touver si c'est un article ou un report
        if '\documentclass{article}' in self.latex_code:
            self.document_class='article'
        elif '\documentclass{report}' in self.latex_code:
            self.document_class='report'
        
#        print self.latex_code
        interest=True
        while interest:
            self.DeleteComments()
            # find important stuff in current line and store columns
            ipn=[] #Interresting points name
            ipi=[] #Interresting points indices 
            # Remove comments

    #        print self.latex_code
            ans=self.FindLatexTag(self.latex_code,'input')
    #        print ans
            if ans!=None:
                ipn.append('input')
                ipi.append(ans)
            ans=self.FindLatexTag(self.latex_code,'scalebox')
            if ans!=None:
                ipn.append('scalebox')
                ipi.append(ans)
            ans=self.FindLatexTag(self.latex_code,'chapter')
            if ans!=None:
                ipn.append('chapter')
                ipi.append(ans)
            ans=self.FindLatexTag(self.latex_code,'section')
            if ans!=None:
                ipn.append('section')
                ipi.append(ans)
            ans=self.FindLatexTag(self.latex_code,'section*')
            if ans!=None:
                ipn.append('section*')
                ipi.append(ans)
            ans=self.FindLatexTag(self.latex_code,'subsection')
            if ans!=None:
                ipn.append('subsection')
                ipi.append(ans)
            ans=self.FindLatexTag(self.latex_code,'subsubsection')
            if ans!=None:
                ipn.append('subsubsection')
                ipi.append(ans)
            ans=self.FindLatexTag(self.latex_code,'lstset')
            if ans!=None:
                ipn.append('lstset')
                ipi.append(ans)
            ans=self.FindLatexEnv(self.latex_code,'lstlisting')
            if ans!=None:
                ipn.append('lstlisting')
                ipi.append(ans)
            ans=self.FindLatexEnv(self.latex_code,'itemize')
            if ans!=None:
                ipn.append('itemize')
                ipi.append(ans)
            ans=find_between(self.latex_code,'$','$')
            if ans!=None:
                ipn.append('dollar')
                ipi.append(self.latex_code.index('$'+ans+'$'))
            ans=find_between(self.latex_code,'\[','\]')
            if ans!=None:
                ipn.append('math')
                ipi.append(self.latex_code.index('\['+ans+'\]'))
            ans=self.FindLatexEnv(self.latex_code,'equation')
            if ans!=None:
                ipn.append('equation')
                ipi.append(ans)
            ans=self.FindLatexEnv(self.latex_code,'tikzpicture')
            if ans!=None:
                ipn.append('tikzpicture')
                ipi.append(ans)
            ans=self.FindLatexTag(self.latex_code,'url')
            if ans!=None:
                ipn.append('url')
                ipi.append(ans)
            ans=self.FindLatexEnv(self.latex_code,'tabular')
            if ans!=None:
                ipn.append('tabular')
                ipi.append(ans)
            ans=self.FindLatexTag(self.latex_code,'changedir')
            if ans!=None:
                ipn.append('changedir')
                ipi.append(ans)


            # get the interesting point with smaller index
            ip=sorted(zip(ipi,ipn))
            print ip
            if len(ip)==0:
                interest=False
                break
    #        print ip
            
            # Execute translation of ip[0]
            if ip[0][1]=='scalebox':
                args=self.FindTagArgs(ip[0][0])
#                print args
                print 'Compiling image'
    
                # Storing code, writing to file
                header_ps=''                
                header_ps+='\documentclass{article}\n'
                header_ps+='\usepackage[utf8x]{inputenc}\n'
                header_ps+= '\usepackage[T1]{fontenc}\n'
                header_ps+='\usepackage[francais]{babel}\n'
    
                header_ps+='\usepackage{graphicx}\n'
                header_ps+='\usepackage[usenames,dvipsnames]{pstricks}\n'
                header_ps+='\usepackage{epsfig}\n'
                header_ps+='\usepackage{pst-grad} % For gradients\n'
                header_ps+='\usepackage{pst-plot} % For axes\n'
                header_ps+='\pagenumbering{gobble}\n'
                header_ps+='\\begin{document}\n'
    
                header_ps+='\scalebox{'+args[0]+'}'+'{'+args[1]+'}\n'
                header_ps+='\end{document}'
                
                WriteFile(header_ps,'pst.tex')
                # Compiling into image
                os.system('latex -interaction=batchmode pst.tex')
                os.system('dvips -q pst.dvi')                
                os.system('convert -trim +repage -density 135 pst.ps image_'+str(self.image_number)+'.png')
                os.remove('pst.tex')
                self.image_number+=1
                self.latex_code=self.latex_code.replace('\scalebox{'+args[0]+'}','<image_'+str(self.image_number)+'>',1)
                self.latex_code=self.latex_code.replace('{'+args[1]+'}','',1)                

            if ip[0][1]=='tikzpicture':
                content=self.FindEnvContent(ip[0][0])
#                print 'content'
#                print content
                content2=content
#                print args
                print 'Compiling image ',self.image_number
    
                # Storing code, writing to file
                header_ps=''                
                header_ps+='\documentclass{article}\n'
                header_ps+='\usepackage[utf8x]{inputenc}\n'
                header_ps+= '\usepackage[T1]{fontenc}\n'
                header_ps+='\usepackage[francais]{babel}\n'
    
                header_ps+='\usepackage{graphicx}\n'
                header_ps+='\usepackage{epsfig}\n'
                header_ps+='\usepackage{pgf}\n'
                header_ps+='\usepackage{tikz}\n'
                header_ps+='\usepackage{schemabloc} \n'
                header_ps+='\usepackage{pgfplots} \n'
                header_ps+='\pagenumbering{gobble}\n'
                header_ps+='\\begin{document}\n'
    
                header_ps+='\scalebox{1.}{\\begin{tikzpicture}\n'+content+'\end{tikzpicture}'+'}\n'
                header_ps+='\end{document}'
                
                WriteFile(header_ps,'pst.tex')
                # Compiling into image
                os.system('latex -interaction=batchmode pst.tex')
                os.system('dvips -q pst.dvi')                
                os.system('convert -trim +repage -density 135 pst.ps image_'+str(self.image_number)+'.png')
                os.remove('pst.tex')
                self.image_number+=1
#                print content2==content
                self.latex_code=self.latex_code.replace('\\begin{tikzpicture}'+content+'\end{tikzpicture}','<image_'+str(self.image_number)+'>',1)
#                self.latex_code=self.latex_code.replace('\\begin{lstlisting}'+content+'\end{lstlisting}','<code class=\''+self.current_language+'\'>'+content+'</code>',1)
#                self.latex_code=self.latex_code.replace('{'+args[1]+'}','',1)                

                
                
            elif ip[0][1]=='input':
                args=self.FindTagArgs(ip[0][0])
                input_file=self.current_directory+args[0]
                if not input_file[-4:]=='.tex':
                    input_file+='.tex'
                print 'inputing file: ',input_file
                old_path=self.current_directory
#                print 'cd',self.current_directory
                new_path=os.path.dirname(os.path.abspath(input_file))+'/'
                input_code='\n\changedir{'+new_path+'} '
#                self.current_directory=new_path                
                input_code+=ReadFile(input_file,output='string')
                input_code+='\n\changedir{'+old_path+'} '
                self.latex_code=self.latex_code.replace('\input{'+args[0]+'}',input_code,1)

            elif ip[0][1]=='chapter':
                args=self.FindTagArgs(ip[0][0])
                if self.document_class=='report':
                    self.latex_code=self.latex_code.replace('\chapter{'+args[0]+'}','{{{#'+args[0]+'}}}',1)
            elif ip[0][1]=='section':
                args=self.FindTagArgs(ip[0][0])
                if self.document_class=='report':
                    self.latex_code=self.latex_code.replace('\section{'+args[0]+'}','{{{##'+args[0]+'}}}',1)
                if self.document_class=='article':
                    self.latex_code=self.latex_code.replace('\section{'+args[0]+'}','{{{#'+args[0]+'}}}',1)
            elif ip[0][1]=='section*':
                args=self.FindTagArgs(ip[0][0])
                if self.document_class=='report':
                    self.latex_code=self.latex_code.replace('\section*{'+args[0]+'}','{{{##'+args[0]+'}}}',1)
                if self.document_class=='article':
                    self.latex_code=self.latex_code.replace('\section*{'+args[0]+'}','{{{#'+args[0]+'}}}',1)

            elif ip[0][1]=='subsection':
                args=self.FindTagArgs(ip[0][0])
                if self.document_class=='report':
                    self.latex_code=self.latex_code.replace('\subsection{'+args[0]+'}','{{{###'+args[0]+'}}}',1)
                if self.document_class=='article':
                    self.latex_code=self.latex_code.replace('\subsection{'+args[0]+'}','{{{##'+args[0]+'}}}',1)

            elif ip[0][1]=='subsubsection':
                args=self.FindTagArgs(ip[0][0])
                if self.document_class=='report':
                    self.latex_code=self.latex_code.replace('\subsubsection{'+args[0]+'}','{{{####'+args[0]+'}}}',1)
                if self.document_class=='article':
                    self.latex_code=self.latex_code.replace('\subsubsection{'+args[0]+'}','{{{###'+args[0]+'}}}',1)
                
            elif ip[0][1]=='lstset':
#                print ip[0][0]
#                print self.latex_code[ip[0][0]:ip[0][0]+30]
                args=self.FindTagArgs(ip[0][0])
#                print args
##                input_code=ReadFile(args[0]+'.tex',output='string')
                if 'language=' in args[0]:                
                    l1=find_between(args[0],'language=',',')
                    l2=find_between(args[0],'language=','}')
                    l=None
                    if l1!=None:
                        l=l1
                    elif l2!=None:
                        l=l2
                    else:
                        i=args[0].index('language=')
                        l=args[0][i+8:]
                    if l!=None:
                        self.current_language=l
#                    print 'cl',self.current_language
                self.latex_code=self.latex_code.replace('\lstset{'+args[0]+'}','',1)

            elif ip[0][1]=='lstlisting':
                content=self.FindEnvContent(ip[0][0])
#                print ':',content,':'
#                input_code=ReadFile(args[0]+'.tex',output='string')
                self.latex_code=self.latex_code.replace('\\begin{lstlisting}'+content+'\end{lstlisting}','<code class=\''+self.current_language+'\'>'+content+'</code>',1)
            
            elif ip[0][1]=='itemize':
                content=self.FindEnvContent(ip[0][0])
                content_tex=content.replace('\item ','-* ')
                self.latex_code=self.latex_code.replace('\\begin{itemize}'+content+'\end{itemize}',content_tex,1)
            elif ip[0][1]=='dollar':
                content=find_between(self.latex_code,'$','$')
                self.latex_code=self.latex_code.replace('$'+content+'$','<mathdollar>'+content+'</mathdollar>',1)    

            elif ip[0][1]=='math':
                content=find_between(self.latex_code,'\[','\]')
                self.latex_code=self.latex_code.replace('\['+content+'\]','<math2dollar>'+content+'</math2dollar>',1)    
                
            elif ip[0][1]=='equation':
                content=self.FindEnvContent(ip[0][0])
                self.latex_code=self.latex_code.replace('\\begin{equation}'+content+'\end{equation}','<math2dollar>'+content+'</math2dollar>',1)
            
            elif ip[0][1]=='url':
                args=self.FindTagArgs(ip[0][0])
                self.latex_code=self.latex_code.replace('\url{'+args[0]+'}','[->'+args[0]+']')            

            elif ip[0][1]=='changedir':
                args=self.FindTagArgs(ip[0][0])
#                print args
                self.current_directory=args[0]
                if (not self.current_directory=='')&(not self.current_directory[-1]=='/'):
                    self.current_directory+='/'
#                print 'current dir: ',self.current_directory
                self.latex_code=self.latex_code.replace('\changedir{'+args[0]+'}','')            

            elif ip[0][1]=='tabular':
                content=self.FindEnvContent(ip[0][0])
#                print 'content: ',content
                options=find_between(content,'{','}')
                tabular_tex=content.replace('{'+options+'}','')
#                options=options.replace('{','')
#                options=options.replace('}','')
#                print content
                cells=self.AnalyseTabular(tabular_tex)
#                print len(cells)
#                print cells
                tabular_spip=''
                for row in cells:
#                    print '---------row'
                    tabular_spip+='|'
                    for cell in row:
#                        print 'cell: ',cell
                        tabular_spip+=cell+'|'
                    tabular_spip+='\n'
                tabular_spip=tabular_spip.replace('\hline','')
#                print 'tabular_spip',tabular_spip
#                print tabular_spip
                self.latex_code=self.latex_code.replace('\\begin{tabular}'+content+'\end{tabular}',tabular_spip)            
#                print self.latex_code

        # Replacement of non-SPIP tags due to latex collision
        self.latex_code=self.latex_code.replace('<mathdollar>','<math>$')
        self.latex_code=self.latex_code.replace('</mathdollar>','$</math>')
        self.latex_code=self.latex_code.replace('<math2dollar>','<math>$$')
        self.latex_code=self.latex_code.replace('</math2dollar>','$$</math>')
            
        # Delete header of latex: 
        bdi=self.FindLatexEnv(self.latex_code,'document')# Begin document index
        if bdi==None:bdi=0
        self.latex_code=self.latex_code.replace(self.latex_code[0:bdi],'')
        self.latex_code=self.latex_code.replace('\\begin{document}','')
        self.latex_code=self.latex_code.replace('\\end{document}','')
        self.latex_code=self.latex_code.replace('\\\n','\n')
        print 'writing file'
        WriteFile(self.latex_code,output_file)
#        WriteFile('r',output_file)

                    
            
t=L2STranslator(input_file,output_file)
t.Translate()
            
#t=L2STranslator('test.tex','output.spip')
