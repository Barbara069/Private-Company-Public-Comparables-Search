"""Fallback: artifact-tool's native XLSX exporter aborted twice after validation."""
import json,pathlib,datetime,re
from openpyxl import Workbook,load_workbook
from openpyxl.styles import Font,PatternFill,Alignment
from openpyxl.utils import get_column_letter
P=pathlib.Path(__file__).resolve().parent/'delivery'
read=lambda n:json.loads((P/(n+'.json')).read_text())
s=read('download_summary');wb=Workbook();wb.remove(wb.active)
summary=[{'Metric':k.replace('_',' '),'Value':v} for k,v in s.items()]
specs=[('Download Summary',summary),('Companies 560',read('Companies_560')),('Coverage 560',read('Coverage_560')),('Annual Financials',read('annual_five_years')),('Latest Quarter',read('latest_quarter')),('LTM',read('ltm')),('Market Snapshot',read('market')),('Business Segments',read('business_segments')),('Geographic Segments',read('geographic_segments')),('Evidence',read('Evidence')),('Field Guide',read('Field_Guide'))]
for name,rows in specs:
    sh=wb.create_sheet(name);sh.sheet_view.showGridLines=False
    cols=list(rows[0]) if rows else ['Status'];sh.append(cols)
    for row in rows:
        vals=[]
        for col in cols:
            v=row.get(col)
            if isinstance(v,str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}',v) and (col.endswith(('.DATE','.CALCDATE')) or 'Employees Date' in col or 'Incorporation Date' in col):v=datetime.datetime.fromisoformat(v)
            if isinstance(v,str) and v.startswith('='):v="'"+v
            vals.append(v)
        sh.append(vals)
    sh.freeze_panes='D2' if len(cols)>4 else 'A2';sh.auto_filter.ref=sh.dimensions
    for cell in sh[1]:
        cell.fill=PatternFill('solid',fgColor='243746');cell.font=Font(name='Arial',size=10,bold=True,color='FFFFFF');cell.alignment=Alignment(wrap_text=True,vertical='center')
    sh.row_dimensions[1].height=45
    for j,key in enumerate(cols,1):
        width=23
        if key in ['Metric','Variable Name']:width=48
        if key=='Value':width=85
        if 'Company Name' in key or key in ['Company Name','Description']:width=36
        if 'Identity Status' in key or key in ['Notes','Source Location']:width=52
        if 'Link' in key:width=58
        if key in ['LSEG Business Summary','Source Text']:width=105
        sh.column_dimensions[get_column_letter(j)].width=width
        for colcells in sh.iter_cols(min_col=j,max_col=j,min_row=2):
            for c in colcells:
                c.font=Font(name='Arial',size=10)
                c.alignment=Alignment(vertical='top',wrap_text=key in ['LSEG Business Summary','Source Text','Notes','Description','Identity Status','Source Location','Variable Name'] or 'Company Name' in key)
                if isinstance(c.value,datetime.datetime):c.number_format='yyyy-mm-dd'
                elif isinstance(c.value,(float,int)) and not isinstance(c.value,bool):
                    if key=='TR.EFFECTIVETAXRATE':c.number_format='0.00"%"'
                    elif key in ['TR.NUMBEROFEMPLOYEES','TR.SHARESOUTSTANDING'] or key.endswith('observations'):c.number_format='#,##0'
                    elif key=='TR.EVTOEBITDA':c.number_format='0.00"x"'
                    else:c.number_format='#,##0.00'
                if 'Link' in key and isinstance(c.value,str) and c.value.startswith('https://'):
                    c.hyperlink=c.value;c.font=Font(name='Arial',size=10,color='0563C1',underline='single')
    for i,row in enumerate(rows,2):
        if name=='Evidence':sh.row_dimensions[i].height=190
        elif name=='Companies 560':sh.row_dimensions[i].height=150
        elif name=='Field Guide':sh.row_dimensions[i].height=42
        else:sh.row_dimensions[i].height=30
    sh.sheet_properties.pageSetUpPr.fitToPage=True
wb.save(P/'560_Company_Data.xlsx')
check=load_workbook(P/'560_Company_Data.xlsx',read_only=True,data_only=True)
assert check['Companies 560'].max_row==561
assert check['Coverage 560'].max_row==561
assert check['Annual Financials'].max_row==2801
assert check['Evidence'].cell(1,5).value=='Source Text' and check['Evidence'].cell(1,6).value=='Source Link'
assert len({r[0] for r in check['Companies 560'].iter_rows(min_row=2,values_only=True)})==560
print('Verified saved workbook:',[(sh.title,sh.max_row-1,sh.max_column) for sh in check]);check.close()
