# filter
Scripts for filtering on reference databases.


## 运行命令

输入以下命令即可对来自 NCBI Genbank 的目标类群（例如某个纲）的序列进行过滤
```
python setup_filter.py <fasta_file> <taxon_file>
```

输入以下命令即可对来自 NCBI Genbank 和 BOLD 的目标类群（例如某个纲）的序列进行过滤
```
python setup_filter.py <fasta_file> <taxon_file> <BOLD_file>
```

## 分类文件获取方式

taxon_file 获取方式（ncbi_id 为目标类群在NCBI的分类号/Taxonomy ID；例如，Collembola 为 30001，详见 [taxonkit官方说明](https://github.com/shenwei356/taxonkit) ）：
```
taxonkit list --show-rank --show-name --indent " " --ids <ncbi_id>
```
