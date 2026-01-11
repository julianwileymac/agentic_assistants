# Chunk: dfebec9d7fb3_4

- source: `webui/.next/server/chunks/ssr/Documents_GitHub_agentic_assistants_webui_6b6ec4ac._.js`
- lines: 14-33
- chunk: 5/7

```
: Content Writer
    goal: Create clear and engaging content
    backstory: Skilled technical writer

# Define tasks
tasks:
  - name: Research Task
    description: Research the given topic thoroughly
    agent: Researcher
    expected_output: A comprehensive research report

  - name: Writing Task
    description: Write a summary based on research
    agent: Writer
    expected_output: A well-written summary document

# Flow settings
process: sequential
verbose: true
`;function w(){let a=(0,d.useRouter)(),r=(0,d.useSearchParams)(),u=r.get("project_id"),w="true"===r.get("import"),[x,y]=c.useState(!1),[z,A]=c.useState("yaml"),[B,C]=c.useState({name:"",description:"",flow_type:"crew",status:"draft",flow_yaml:v,tags:"",project_id:u||""});c.useEffect(()=>{},[w]);let D=async b=>{if(b.preventDefault(),!B.name.trim())return void t.toast.error("Flow name is required");y(!0);try{let b=await fetch("http://localhost:8080/api/v1/flows",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name:B.name.trim(),description:B.description.trim(),flow_type:B.flow_type,status:B.status,flow_yaml:B.flow_yaml,project_id:B.project_id||null,agents:[],tags:B.tags.split(",").map(a=>a.trim()).filter(Boolean),metadata:{}})});if(b.ok){let c=await b.json();t.toast.success("Flow created successfully"),a.push(`/flows/${c.id}`)}else{let a=await b.json();t.toast.error(a.detail||"Failed to create flow")}}catch(a){t.toast.error("Failed to create flow")}finally{y(!1)}};return(0,b.jsxs)("div",{className:"max-w-4xl mx-auto space-y-6",children:[(0,b.jsxs)("div",{className:"flex items-center gap-4",children:[(0,b.jsx)(m.Button,{variant:"ghost",size:"icon",asChild:!0,children:(0,b.jsx)(e.default,{href:"/flows",children:(0,b.jsx)(f.ArrowLeft,{className:"size-4"})})}),(0,b.jsxs)("div",{children:[(0,b.jsx)("h1",{className:"text-3xl font-bold tracking-tight",children:"New Flow"}),(0,b.jsx)("p",{className:"text-muted-foreground",children:"Create a multi-agent workflow"})]})]}),(0,b.jsxs)("form",{onSubmit:D,children:[(0,b.jsxs)("div",{className:"grid grid-cols-1 lg:grid-cols-3 gap-6",children:[(0,b.jsxs)(l.Card,{className:"lg:col-span-1",children:[(0,b.jsxs)(l.CardHeader,{children:[(0,b.jsx)(l.CardTitle,{children:"Flow Details"}),(0,b.jsx)(l.CardDescription,{children:"Basic flow information"})]}),(0,b.jsxs)(l.CardContent,{className:"space-y-4",children:[(0,b.jsxs)("div",{className:"space-y-2",children:[(0,b.jsx)(o.Label,{htmlFor:"name",children:"Flow Name *"}),(0,b.jsx)(n.Input,{id:"name",placeholder:"Research Pipeline",value:B.name,onChange:a=>C({...B,name:a.target.value}),required:!0})]}),(0,b.jsxs)("div",{className:"space-y-2",children:[(0,b.jsx)(o.Label,{htmlFor:"description",children:"Description"}),(0,b.jsx)(p.Textarea,{id:"description",placeholder:"Describe your flow...",rows:3,value:B.description,onChange:a=>C({...B,description:a.target.value})})]}),(0,b.jsxs)("div",{className:"space-y-2",children:[(0,b.jsx)(o.Label,{htmlFor:"flow_type",children:"Flow Type"}),(
```
