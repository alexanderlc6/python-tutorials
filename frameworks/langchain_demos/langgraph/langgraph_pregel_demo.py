from langgraph.channels import EphemeralValue, LastValue, Topic, BinaryOperatorAggregate
from langgraph.pregel import Pregel, NodeBuilder, ChannelWriteEntry

node1 = (NodeBuilder()
         .subscribe_only('a')
         .do(lambda x: x+x)
         .write_to('b'))

node2 = (NodeBuilder()
         .subscribe_to('b')
         .do(lambda x: x['b']+x['b'])
         .write_to('c'))

app = Pregel(nodes={'node1': node1, 'node2': node2},
             channels={
                'a': EphemeralValue(str),
                'b': LastValue(str),
                'c': EphemeralValue(str)
            },
            input_channels = ['a'],
            output_channels = ['b', 'c']
)

print(app.invoke({'a': 'foo'}))

# Using a Topic channel
node1 = (
    NodeBuilder().subscribe_only("a")
    .do(lambda x: x + x)
    .write_to("b", "c")
)

node2 = (
    NodeBuilder().subscribe_only("b")
    .do(lambda x: x + x)
    .write_to("c")
)

app = Pregel(
    nodes={"node1": node1, "node2": node2},
    channels={
        "a": EphemeralValue(str),
        "b": EphemeralValue(str),
        "c": Topic(str, accumulate=True),
    },
    input_channels=["a"],
    output_channels=["c"],
)

print(app.invoke({"a": "foo"}))

# Using a BinaryOperatorAggregate channel
# node1 = (
#     NodeBuilder().subscribe_only("a")
#     .do(lambda x: x + x)
#     .write_to("b", "c")
# )
#
# node2 = (
#     NodeBuilder().subscribe_only("b")
#     .do(lambda x: x + x)
#     .write_to("c")
# )
#
# def reducer(current, update):
#     if current:
#         return current + '|' + update
#     else:
#         return update
#
# app = Pregel(
#     nodes={"node1": node1, "node2": node2},
#     channels={
#         "a": EphemeralValue(str),
#         "b": EphemeralValue(str),
#         "c": BinaryOperatorAggregate(str, operator=reducer())
#     },
#     input_channels=["a"],
#     output_channels=["c"],
# )
# print(app.invoke({"a": "foo"}))
#
# # Introducing a cycle
# node3 = (
#     NodeBuilder().subscribe_only('value')
#     .do(lambda x: x + x if len(x) < 10 else None)
#     .write_to(ChannelWriteEntry(channel='value', skip_none=True))
# )
#
# app = Pregel(nodes = { 'node3': node3},
#              channels={'value': EphemeralValue(str)},
#              input_channels=['value'],
#              output_channels=['value']
# )
#
# print(app.invoke({'value': 'a'}))
