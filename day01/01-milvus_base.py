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

def operate_entity():
    # # todo:1. 创建集合collection
    # 这种方式: collection 只包括两个字段. id 作为主键， vector 作为向量字段，以及自动设置 auto_id、enable_dynamic_field 为 True
    # auto_id 启用此设置可确保主键自动递增。在数据插入期间无需手动提供主键。
    # enable_dynamic_field 启用后，要插入的数据中除 id 和 vector 之外的所有字段都将被视为动态字段。
    # # 这些附加字段作为键值对保存在名为 $meta 的特殊字段中。此功能允许在数据插入期间包含额外的字段。
    # client.create_collection(collection_name='demo_v2', dimension=5, metric_type='IP')
    #
    # # todo:2. 插入数据（也叫实体）
    data = [
        {"id": 0, "vector": [0.3580376395471989, -0.6023495712049978, 0.18414012509913835, -0.26286205330961354,
                             0.9029438446296592], "color": "pink_8682"},
        {"id": 1, "vector": [0.19886812562848388, 0.06023560599112088, 0.6976963061752597, 0.2614474506242501,
                             0.838729485096104], "color": "red_7025"},
        {"id": 2, "vector": [0.43742130801983836, -0.5597502546264526, 0.6457887650909682, 0.7894058910881185,
                             0.20785793220625592], "color": "orange_6781"},
        {"id": 3, "vector": [0.3172005263489739, 0.9719044792798428, -0.36981146090600725, -0.4860894583077995,
                             0.95791889146345], "color": "pink_9298"},
        {"id": 4, "vector": [0.4452349528804562, -0.8757026943054742, 0.8220779437047674, 0.46406290649483184,
                             0.30337481143159106], "color": "red_4794"},
        {"id": 5, "vector": [0.985825131989184, -0.8144651566660419, 0.6299267002202009, 0.1206906911183383,
                             -0.1446277761879955], "color": "yellow_4222"},
        {"id": 6, "vector": [0.8371977790571115, -0.015764369584852833, -0.31062937026679327, -0.562666951622192,
                             -0.8984947637863987], "color": "red_9392"},
        {"id": 7, "vector": [-0.33445148015177995, -0.2567135004164067, 0.8987539745369246, 0.9402995886420709,
                             0.5378064918413052], "color": "grey_8510"},
        {"id": 8, "vector": [0.39524717779832685, 0.4000257286739164, -0.5890507376891594, -0.8650502298996872,
                             -0.6140360785406336], "color": "white_9381"},
        {"id": 9, "vector": [0.5718280481994695, 0.24070317428066512, -0.3737913482606834, -0.06726932177492717,
                             -0.6980531615588608], "color": "purple_4976"}
    ]
    # schema = client.create_schema(auto_id=False, enable_dynamic_field=True)
    # schema.add_field(field_name='id', datatype=DataType.INT64, is_primary=True)
    # schema.add_field(field_name='vector', datatype=DataType.FLOAT_VECTOR, dim=5)
    # index_param = client.prepare_index_params()
    # index_param.add_index(field_name='vector', index_name='vector_index', index_type='', metric_type='L2')
    # client.create_collection(collection_name='demo_v2', schema=schema, index_params=index_param)

    # client.insert(collection_name='demo_v2', data=data)

    ## todo:2.1 将数据插入到特定分区，可以在插入请求中指定分区名称，如下所示：
    data = [
        {"id": 10, "vector": [-0.5570353903748935, -0.8997887893201304, -0.7123782431855732, -0.6298990746450119,
                              0.6699215060604258], "color": "red_1202"},
        {"id": 11, "vector": [0.6319019033373907, 0.6821488267878275, 0.8552303045704168, 0.36929791364943054,
                              -0.14152860714878068], "color": "blue_4150"},
        {"id": 12, "vector": [0.9483947484855766, -0.32294203351925344, 0.9759290319978025, 0.8262982148666174,
                              -0.8351194181285713], "color": "orange_4590"},
        {"id": 13, "vector": [-0.5449109892498731, 0.043511240563786524, -0.25105249484790804, -0.012030655265886425,
                              -0.0010987671273892108], "color": "pink_9619"},
        {"id": 14, "vector": [0.6603339372951424, -0.10866551787442225, -0.9435597754324891, 0.8230244263466688,
                              -0.7986720938400362], "color": "orange_4863"},
        {"id": 15, "vector": [-0.8825129181091456, -0.9204557711667729, -0.935350065513425, 0.5484069690287079,
                              0.24448151140671204], "color": "orange_7984"},
        {"id": 16, "vector": [0.6285586391568163, 0.5389064528263487, -0.3163366239905099, 0.22036279378888013,
                              0.15077052220816167], "color": "blue_9010"},
        {"id": 17, "vector": [-0.20151825016059233, -0.905239387635804, 0.6749305353372479, -0.7324272081377843,
                              -0.33007998971889263], "color": "blue_4521"},
        {"id": 18, "vector": [0.2432286610792349, 0.01785636564206139, -0.651356982731391, -0.35848148851027895,
                              -0.7387383128324057], "color": "orange_2529"},
        {"id": 19, "vector": [0.055512329053363674, 0.7100266349039421, 0.4956956543575197, 0.24541352586717702,
                              0.4209030729923515], "color": "red_9437"}
    ]

    # client.create_partition(collection_name='demo_v2', partition_name='partitionA')
    # res = client.insert(collection_name='demo_v2', data=data, partition_name='partitionA')
    # print(res)

    ## todo:4. 更新插入数据
    # 在 Milvus 中，upsert 操作执行数据级操作，根据集合中是否已存在主键来插入或更新实体。具体来说：
    # 如果集合中已存在该实体的主键，则现有实体将被覆盖。
    # 如果集合中不存在主键，则将插入一个新实体。
    data = [
        {"id": 0, "vector": [-0.619954382375778, 0.4479436794798608, -0.17493894838751745, -0.4248030059917294,
                             -0.8648452746018911], "color": "black_9898"},
        {"id": 1, "vector": [0.4762662251462588, -0.6942502138717026, -0.4490002642657902, -0.628696575798281,
                             0.9660395877041965], "color": "red_7319"},
        {"id": 2, "vector": [-0.8864122635045097, 0.9260170474445351, 0.801326976181461, 0.6383943392381306,
                             0.7563037341572827], "color": "white_6465"},
        {"id": 3, "vector": [0.14594326235891586, -0.3775407299900644, -0.3765479013078812, 0.20612075380355122,
                             0.4902678929632145], "color": "orange_7580"},
        {"id": 4, "vector": [0.4548498669607359, -0.887610217681605, 0.5655081329910452, 0.19220509387904117,
                             0.016513983433433577], "color": "red_3314"},
        {"id": 5, "vector": [0.11755001847051827, -0.7295149788999611, 0.2608115847524266, -0.1719167007897875,
                             0.7417611743754855], "color": "black_9955"},
        {"id": 6, "vector": [0.9363032158314308, 0.030699901477745373, 0.8365910312319647, 0.7823840208444011,
                             0.2625222076909237], "color": "yellow_2461"},
        {"id": 7, "vector": [0.0754823906014721, -0.6390658668265143, 0.5610517334334937, -0.8986261118798251,
                             0.9372056764266794], "color": "white_5015"},
        {"id": 8, "vector": [-0.3038434006935904, 0.1279149203380523, 0.503958664270957, -0.2622661156746988,
                             0.7407627307791929], "color": "purple_6414"},
        {"id": 9, "vector": [-0.7125086947677588, -0.8050968321012257, -0.32608864121785786, 0.3255654958645424,
                             0.26227968923834233], "color": "brown_7231"}
    ]

    # res = client.upsert(collection_name='demo_v2', data=data)
    # print(res)
    # res = client.upsert(collection_name='demo_v2', data=data, partition_name='partitionA')
    # print(res)

    # todo:5. 删除实体（数据）
    # 按照过滤器删除；如果不指定分区，默认情况下会在整个集合中进行删除
    # res = client.delete(collection_name='demo_v2', filter='id in [12,5,6]')
    # print(res)
    res = client.delete(collection_name='demo_v2', ids=[1,2,3,4], partition_name='partitionA')
    print(res)



if __name__ == '__main__':
    # operate_db()
    # operate_collection()
    # operate_entity()