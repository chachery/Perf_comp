# filter
The filtration method aims to accomplish redundancy removal on highly similar sequences.
如果觉得（某个类群的）参考数据库过大影响比对/建树速度，可以用本过滤方法去除该类群各个物种中相似度较高的冗余序列。



## 运行命令

输入以下命令即可对来自 NCBI Genbank 的目标类群（例如某个纲）的序列进行过滤
```
python setup_filter.py <fasta_file> <taxon_file>
```

输入以下命令即可对来自 NCBI Genbank 和 BOLD 的目标类群（例如某个纲）的序列进行过滤
```
python setup_filter.py <fasta_file> <taxon_file> <BOLD_file>
```

## 分类信息文件获取方式

taxon_file 为目标类群在 NCBI Genbank 上的分类信息文件（ncbi_id 为目标类群在NCBI的分类号/Taxonomy ID；例如，Collembola 为 30001，详见 [taxonkit](https://github.com/shenwei356/taxonkit) 官方说明），获取方法为：
```
taxonkit list --show-rank --show-name --indent " " --ids <ncbi_id>
```

BOLD_file 为目标类群在 BOLD 上的分类信息文件，获取方法为：
```
python treatBOLD.py <input_tsv> <output>
```
其中，input_tsv 为从BOLD下载的目标类群的tsv格式的分类信息表格文件，output为输出的 BOLD_file 文件名。
该脚本运行时可能会遇到乱码错误，这是分类信息表格文件中人名带有的特殊字符引起的，运行以下命令再获取 BOLD_file 即可：
```
python rm_failDecode.py <input_tsv>
```

## config.py 配置文件

config.py内可以设置和修改过滤相关的参数：

threshold_inter 代表过滤的最低相似度阈值，默认为0.97；

REF_HS 代表过滤参考文件，该参数的设置初衷主要是为了方便筛选条形码标记指定片段上的序列（如COI的658bp标准片段），该文件内需要放置多条目标类群在指定片段上的序列。如果设置了该值，过滤就会在设置的参考文件基础上，依据相似度（SIMILARITY_THRESHOLD_HS）和覆盖率（COVERAGE_THRESHOLD_HS）进行。

如果 IS_TRIM 设置了 True，那么过滤后的序列会依据参考文件（REF_HS）内的序列进行剪切。
