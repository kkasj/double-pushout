# Installation

1. `pip install -r requirements.txt`
2. `python main.py`
3. Open http://localhost:8050/ in your browser

# Usage

1. Create the host graph by adding nodes and edges:
    - Click the "Add Node" button to add a node
    - Click the "Add Edge" button to add edges between all selected nodes (to select multiple nodes: SHIFT + click)
2. Create a rule by clicking the "Create Rule" button:
    - You can select nodes and edges from the host graph before clicking "Create Rule" button to automatically add them to the rule
3. Modify the L graph appropriately 
4. Select the K subgraph:
    - Select nodes and edges from the L graph
    - Click the "Select K" button
5. Modify the R graph appropriately
6. Click the "Finalize Rule" button to save the rule
7. Repeat steps 2-6 to create additional rules
8. Click the "Apply Rules" button to apply the saved rules to the host graph sequentially
