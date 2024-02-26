#! /bin/bash
source_file=$1
split -l 50 $source_file data/part-

output="["

for part in $(ls data/part-*); do
    part_data="{
        \"Title\": \"$1 man page\",
        \"Data\": \"$(cat $part | sed "s/\“/'/g" | sed "s/\”/'/g")\" |sed "s/[/\\[/g")\"  ,
        \"Source\": \"$1\"
      }"
    output="$output,$part_data"
done

output="$output ]"

echo $output > output.json
rm data/part-*