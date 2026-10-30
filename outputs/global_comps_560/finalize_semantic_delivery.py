import pathlib,subprocess,time
P=pathlib.Path(__file__).resolve().parent
log=pathlib.Path('/tmp/4511-semantic-infer.log')
while 'NLI COMPLETE' not in log.read_text():time.sleep(20)
print('Inference complete. Materializing results.',flush=True)
subprocess.run(['/tmp/4511-lseg-env/bin/python',str(P/'resolve_semantic_validation.py')],check=True)
node='/Users/bai/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
subprocess.run([node,'/Users/bai/.codex/plugins/cache/openai-primary-runtime/spreadsheets/26.1025.11240/skills/spreadsheets/container_tools/mark_artifact_operation_started.mjs','--operation-kind','create','--expected-output-count','1','--output-format','xlsx'],check=True)
subprocess.run([node,'--max-old-space-size=12288',str(P/'build_semantic_validation.mjs')],check=True)
subprocess.run(['/Users/bai/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3',str(P/'package_semantic_validation.py')],check=True)
print('DELIVERY_READY',flush=True)
