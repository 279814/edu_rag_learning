from pymilvus import MilvusClient, DataType


def operate_db():
    client = MilvusClient(uri='http://43.172.89.43:19530', user='root', password='5871258712')
    databases = client.list_databases()
    print(databases)
    if "milvus_demo" not in databases:
        client.create_database(db_name='milvus_demo')
        client.use_database(db_name='milvus_demo')
    else:
        client.use_database(db_name='milvus_demo')
    return client

client = operate_db()

def operate_collection():
    # schema = client.create_schema(auto_id=False, enable_dynamic_field=True)
    # schema.add_field(field_name='id', datatype=DataType.INT64, is_primary=True)
    # schema.add_field(field_name='vector', datatype=DataType.FLOAT_VECTOR, dim=5)
    # schema.add_field(field_name='scalar', datatype=DataType.VARCHAR, max_length=256, description='标量字段')
    # client.create_collection(collection_name='demo_v1', schema=schema)
    #
    # #创建索引
    # index_param = client.prepare_index_params()
    # index_param.add_index(field_name='vector', index_name='vector_index', index_type='', metric_type='COSINE')
    # client.create_index(collection_name='demo_v1', index_params=index_param)

    # #查看索引信息
    # res = client.list_indexes(collection_name='demo_v1')
    # print(res)
    # res = client.describe_index(collection_name='demo_v1', index_name='vector_index')
    # print(res)

    # #加载集合
    # client.load_collection(collection_name='demo_v1')
    # print(client.get_load_state(collection_name='demo_v1'))
    # #删除index
    # client.release_collection(collection_name='demo_v1')
    # client.drop_index(collection_name='demo_v1', index_name='vector_index')

    #标量索引
    index_param = client.prepare_index_params()
    index_param.add_index(field_name='scalar', index_name='scalar_index', index_type='')
    client.create_index(collection_name='demo_v1', index_params=index_param)
    res = client.list_indexes(collection_name='demo_v1')
    print(res)
    res = client.describe_index(collection_name='demo_v1', index_name='scalar_index')
    print(res)



if __name__ == '__main__':
    # operate_db()
    # operate_collection()