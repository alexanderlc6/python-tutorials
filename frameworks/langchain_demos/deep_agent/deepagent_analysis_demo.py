from daytona import Daytona
from daytona import Daytona
from deepagents import create_deep_agent
from langchain_core.stores import InMemoryStore
from langchain_daytona import DaytonaSandbox

sandbox = Daytona().create()
backend = DaytonaSandbox(sandbox=sandbox)

# Other backend
from deepagents.backends import StateBackend, FilesystemBackend, LocalShellBackend

backend=(lambda rt: StateBackend(rt))
backend = FilesystemBackend(root_dir='.', virtual_mode=True)
backend = LocalShellBackend(root_dir='.', env = {'PATH': '/usr/bin:/bin'})

# Verify the sandbox is ready
result = backend.execute('echo ready.')
print(result)

# Upload sample data
import csv
import io
# Create sample sales data
data = [
    ['Date', 'Product', "Units Sold", "Revenue"],
    ["2025-08-01", "Widget A", 10, 250],
    ["2025-08-02", "Widget B", 5, 125],
    ["2025-08-03", "Widget A", 7, 175],
    ["2025-08-04", "Widget C", 3, 90],
    ["2025-08-05", "Widget B", 8, 200]
]

# Convert to CSV bytes
text_buf = io.StringIO()
writer = csv.writer(text_buf)
writer.writerow(data)
csv_bytes = text_buf.getvalue().encode('utf-8')
text_buf.close()

# Upload to backend
backend.upload_files([('./test.csv', csv_bytes)])

agent = create_deep_agent(backend=backend, store=InMemoryStore())

agent.invoke()