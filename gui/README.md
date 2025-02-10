# UI layout

## Page 1: Funnel builder page

Top section: Nodes collection:

- Left: two tables

  - Top table: Input nodes
    - show columns for all fields of input nodes
    - always sync with current list of input nodes
  - Bottom table: calculated nodes - show columns for all fields of calculated nodes
    Whenever the table is updated, the nodes_collection is updated.

- Right: Mermaid chart generated

## Page 2: Charting

Give me a page with a button that says "refresh", and then a plotly chart that's returned from `funnel.get_tornado_chart()`. Give me one sample and i can take care of the rest.

## Page 3: nodes

Text box showing the up to date nodes_collection JSON.
I'd like this box to be in sync with the current status of the nodes_collection, but also editable. If the user edits the JSON, the nodes_collection should be updated accordingly. I'll use this box to allow users to paste in their saved nodes_collection.
