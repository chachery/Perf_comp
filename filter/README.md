# filter
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
