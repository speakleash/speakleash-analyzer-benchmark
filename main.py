import argparse
import pyfiglet
from speakleash import Speakleash
import os
import json
from postprocessor.analyzer import Analyzer
from lm_dataformat import Archive, Reader
import glob
import shutil
import spacy
from rich import print as rich_print
from common.functions import log
from multiprocessing import Pool, set_start_method
from datetime import datetime
import threading

def pool_dummy():
    return

def process_doc(doc):
    counter = doc[0]
    txt, meta = doc[1]
    analyzer = Analyzer(txt, meta, nlp, counter)
    meta = analyzer.go()
    return txt, meta

def initialize_worker():

    print('Initializing worker...')   

    global nlp    
    nlp = spacy.load("pl_core_news_md", disable=('ner','textcat','entity_linker'))
    


if __name__ == '__main__':

    set_start_method("spawn")

    VERSION = "0.1.1"

    base_dir = os.path.join(os.path.dirname(__file__))

    parser = argparse.ArgumentParser(
        prog="SpeakLeash benchmark",
        description="Application performing benchmark of processing Speakleash datasets",
    )

    parser.add_argument("--large", action="store_true", help="Use large docs")
    parser.add_argument("--processes", type=int, help="Number of prcocesses used for metrics counting. Default = os.cpu_count()")
    parser.add_argument("--num_pass", type=int, help="Number of iterations. Default = 1")

    args = parser.parse_args()

 

    if not args.processes:
        args.processes=os.cpu_count()
    
    if not args.num_pass or args.num_pass < 1:
        args.num_pass = 1

 

    figlet = pyfiglet.Figlet(font="slant")
    ascii_banner = figlet.renderText("SpeakLeash")
    print(ascii_banner)
    rich_print("BENCHMARK [blue]v" + VERSION + "[/blue]\n") 

    if args.large:
        rich_print("Dataset document size: [green]" + "LARGE" + "[/green]")
        target_zst_name='benchmark_lg'
    else:
        rich_print("Dataset document size: [green]" + "SMALL" + "[/green]")
        target_zst_name='benchmark_sm'

        

    rich_print("Number of processes: [green]" + str(args.processes) + "[/green]")
    print("")
    log("Starting benchmark", "INFO")
   
    
     
    with open(os.path.join(base_dir, 'Assets' ,target_zst_name + '.manifest'), 'r' ) as f:
        manifest = json.load(f)

    
    file_name_zst = os.path.join(base_dir, target_zst_name + '.jsonl.zst')
    file_name_manifest = os.path.join(base_dir, target_zst_name + '.manifest') 

    rdr = Reader(os.path.join(base_dir, 'Assets' ,target_zst_name + '.jsonl.zst'))            

    

    with Pool(initializer=initialize_worker, processes=args.processes) as pool:

        #Enforce initializers to start before starting timer
        log("Initializing", "INFO")
        dummy_results = [pool.apply_async(pool_dummy) for _ in range(args.processes)]
        for result in dummy_results:
            result.get()
        
        log("Starting benchmark", "INFO")
        time_start = datetime.now()
        
        for i in range(args.num_pass):
            log("Pass #"+str(i+1), "INFO")
            stats = {'documents': 0}
        
            ar = Archive(os.path.join(base_dir, "data"))

            
        
            for txt, meta in pool.imap(func=process_doc, iterable=enumerate(rdr.stream_data(get_meta=True)), chunksize=1):               

                stats['documents'] += 1                        
                
                for key in meta.keys():
                    if not isinstance(meta[key], str):
                        stats[key] = stats.setdefault(key, 0) + meta[key]
                ar.add_data(txt, meta = meta)                

            
        d = datetime.now() - time_start
        elapsed = d.total_seconds()/args.num_pass
        log("Average processing time: " + str(elapsed) + " s", "INFO")

        pool.close()
        pool.join()
        ar.commit()

        

    for key in stats.keys():
        if key in Analyzer.AVG_METRICS_DEF:
            stats[key] = round(stats[key]/stats['documents'],6)

            
    ar = None
    data_files= glob.glob(os.path.join(base_dir,'data','*'))
    file_size = 0

    for f in data_files:
        if f.endswith('.zst'):
            shutil.copy(f, file_name_zst)
            file_size = os.path.getsize(file_name_zst)
            os.remove(f)

    manifest['stats'] = stats
    manifest['file_size'] = file_size

    json_manifest = json.dumps(manifest, indent = 4) 
    with open(file_name_manifest, 'w') as mf:
        mf.write(json_manifest)

           

    if os.path.exists(os.path.join('data')):
        shutil.rmtree(os.path.join('data'))

    log("Benchmark finished", "INFO")
    print("")
