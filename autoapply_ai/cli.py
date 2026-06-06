import argparse, webbrowser
from rich.console import Console
from rich.table import Table
from .database import init_db
from .profile_store import load_profile, save_profile, DEFAULT_PROFILE
from .job_sources import fetch_jobs
from .demo_data import DEMO_JOBS
from .storage import upsert_jobs, score_all_jobs, ranked_jobs, update_status
from .relevance import build_queries
from .prep import save_prep_packet
console=Console()
def cmd_init(args): init_db(); save_profile(DEFAULT_PROFILE); console.print('[green]Initialized database and demo profile.[/green]')
def cmd_quickstart(args):
    init_db(); profile=load_profile(args.session); queries=[args.query] if args.query else build_queries(profile)[:args.query_count]; total=0; errors=[]
    for q in queries:
        jobs,errs=fetch_jobs(q,args.limit,sources=args.sources.split(','), strict=not args.broad); total+=upsert_jobs(jobs); errors+=errs
    if args.demo or total==0: total+=upsert_jobs(DEMO_JOBS); console.print('[cyan]Loaded demo jobs so the app has usable results.[/cyan]')
    df=score_all_jobs(profile,min_score=args.min_score); console.print(f'[green]Ready. {len(df)} relevant jobs scored.[/green]')
    show_table(df.head(args.show)); [console.print(f'[yellow]{e}[/yellow]') for e in errors]
def show_table(df):
    table=Table(title='Top Job Matches')
    for c in ['id','match_score','priority','classification','company','title','location','status']: table.add_column(c)
    for _,r in df.iterrows(): table.add_row(*[str(r.get(c,''))[:45] for c in ['id','match_score','priority','classification','company','title','location','status']])
    console.print(table)
def cmd_fetch(args):
    profile=load_profile(args.session); total=0; errors=[]
    for q in ([args.query] if args.query else build_queries(profile)[:args.query_count]):
        jobs,errs=fetch_jobs(q,args.limit,sources=args.sources.split(','), strict=not args.broad); total+=upsert_jobs(jobs); errors+=errs
    if args.demo: total+=upsert_jobs(DEMO_JOBS)
    console.print(f'[green]Saved {total} new jobs.[/green]'); [console.print(f'[yellow]{e}[/yellow]') for e in errors]
def cmd_score(args): profile=load_profile(args.session); df=score_all_jobs(profile,min_score=args.min_score); console.print(f'[green]Scored jobs. {len(df)} relevant matches.[/green]')
def cmd_top(args): show_table(ranked_jobs(args.session,args.min_score,args.include_rejects).head(args.limit))
def cmd_open(args):
    df=ranked_jobs(args.session,include_rejects=True); row=df[df['id']==args.job_id]
    if row.empty: console.print('[red]Job not found.[/red]'); return
    webbrowser.open(row.iloc[0]['url']); update_status(args.session,args.job_id,'Viewed'); console.print('[green]Opened apply link and marked Viewed.[/green]')
def cmd_status(args): update_status(args.session,args.job_id,args.status,args.notes); console.print('[green]Updated status.[/green]')
def cmd_packet(args):
    profile=load_profile(args.session); df=ranked_jobs(args.session,include_rejects=True); row=df[df['id']==args.job_id]
    if row.empty: console.print('[red]Job not found.[/red]'); return
    console.print(f'[green]Saved prep packet:[/green] {save_prep_packet(row.iloc[0].to_dict(),profile)}')
def build_parser():
    p=argparse.ArgumentParser(description='AutoApply AI Pro v7'); sub=p.add_subparsers(required=True)
    for name,func in [('init',cmd_init),('quickstart',cmd_quickstart),('fetch',cmd_fetch),('score',cmd_score),('top',cmd_top),('open',cmd_open),('status',cmd_status),('packet',cmd_packet)]:
        sp=sub.add_parser(name); sp.set_defaults(func=func); sp.add_argument('--session',default='demo-user')
        if name in ['quickstart','fetch']: sp.add_argument('--query',default=''); sp.add_argument('--limit',type=int,default=50); sp.add_argument('--query-count',type=int,default=4); sp.add_argument('--sources',default='Remotive,Arbeitnow,RemoteOK'); sp.add_argument('--demo',action='store_true'); sp.add_argument('--broad',action='store_true',help='Allow adjacent roles beyond strict data/analytics titles')
        if name in ['quickstart','score','top']: sp.add_argument('--min-score',type=float,default=55)
        if name=='quickstart': sp.add_argument('--show',type=int,default=10)
        if name=='top': sp.add_argument('--limit',type=int,default=10); sp.add_argument('--include-rejects',action='store_true')
        if name in ['open','status','packet']: sp.add_argument('--job-id',type=int,required=True)
        if name=='status': sp.add_argument('--status',required=True); sp.add_argument('--notes',default='')
    return p
def main(): args=build_parser().parse_args(); args.func(args)
