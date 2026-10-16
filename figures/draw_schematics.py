"""Draw the four staged-model schematics as direct vector PDFs."""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
from matplotlib import font_manager
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
from plot_font import regular_libertine,PDF_METADATA
HERE=Path(__file__).resolve().parent
font_manager.fontManager.addfont(str(regular_libertine(HERE)))
plt.rcParams.update({"font.family":"Linux Libertine","font.size":9,
                     "mathtext.fontset":"stix","pdf.fonttype":42,"ps.fonttype":42})
def canvas(size,ylim):
    fig,ax=plt.subplots(figsize=size)
    fig.subplots_adjust(left=.015,right=.985,bottom=.025,top=.975)
    ax.set(xlim=(0,8),ylim=ylim);ax.set_axis_off()
    return fig,ax
def box(ax,x,y,w,h,text):
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle="round,pad=.025",
                              facecolor="white",edgecolor="black",linewidth=.7,zorder=3))
    ax.text(x,y,text,ha="center",va="center",zorder=4)
def arrow(ax,start,end,label=None,at=None,dash=False):
    ax.add_patch(FancyArrowPatch(start,end,arrowstyle="-|>",mutation_scale=9,
                                linewidth=.7,linestyle="--" if dash else "-",color="black"))
    if label:ax.text(*at,label,ha="center",va="center",
                     bbox=dict(facecolor="white",edgecolor="none",pad=1.3))
def save(fig,ax,out,name):
    fig.canvas.draw()
    for label in ax.texts:
        b=label.get_window_extent()
        if b.x0<fig.bbox.x0-1 or b.y0<fig.bbox.y0-1 or b.x1>fig.bbox.x1+1 or b.y1>fig.bbox.y1+1:
            raise ValueError("Label outside canvas: "+label.get_text())
    fig.savefig(out/(name+".pdf"),metadata=PDF_METADATA);plt.close(fig)
def diamond(out):
    fig,ax=canvas((5.4,3.15),(0,4.3))
    box(ax,4,3.25,2.4,.6,"$p_0$, $\\rho=2$\n$(u\\wedge1)\\vee0$")
    box(ax,1.65,1.95,2.2,.6,"$p_1$, $\\rho=1$\n$u\\vee0$")
    box(ax,6.35,1.95,2.2,.6,"$p_2$, $\\rho=1$\n$u\\wedge1$")
    box(ax,4,.55,2.4,.6,"$p_3$, $\\rho=0$\n$u$")
    arrow(ax,(3,2.93),(2.15,2.28),"$H$: simplify-and",(1.8,2.82))
    arrow(ax,(5,2.93),(5.85,2.28),"$Q$: simplify-or",(6.2,2.82))
    arrow(ax,(2.12,1.62),(3,.89),"$Q$: finish-or",(1.9,1.13))
    arrow(ax,(5.88,1.62),(5,.89),"$H$: finish-and",(6.15,1.13))
    ax.text(4,4,"Facts: $\\varnothing,H,Q,HQ$; forward discovers $H$, prophecy discovers $Q$",
            ha="center",va="center")
    save(fig,ax,out,"running-diamond")
def commute(out):
    fig,ax=canvas((5.4,2.1),(-.6,2.75))
    box(ax,1.8,2.15,2.4,.55,"$(p,x)$")
    box(ax,6,2.15,2.7,.55,"$(p,C_p(x))$")
    box(ax,1.8,.55,2.4,.55,"$(q,\\tau_r(x))$")
    box(ax,6,.55,3.2,.55,"$(q,C_q(\\tau_r(x)))$")
    arrow(ax,(3.03,2.15),(4.62,2.15),"analysis closure",(3.82,2.52))
    arrow(ax,(1.8,1.85),(1.8,.85),"$r$",(.98,1.35))
    arrow(ax,(3.03,.55),(4.37,.55),"$C_q$",(3.7,.2))
    arrow(ax,(6,1.85),(6,.85),"$r$ then $C_q$",(6.9,1.35))
    ax.text(4,-.34,"$C_q(\\tau_r(x))=C_q(\\tau_r(C_p(x)))$ for enabled $r$",
            ha="center",va="center")
    save(fig,ax,out,"commute-square")
def pipeline(out):
    fig,ax=canvas((5.4,1.95),(-.4,2.75))
    box(ax,1.1,2,1.9,.65,"Finite JSON\ninstance")
    box(ax,3.9,2,2,.65,"Generator\nexplores graph")
    box(ax,6.8,2,2.15,.65,"Full/saturated proof\nor terminal fork")
    box(ax,5.5,.35,4.7,.7,"Standalone replay verifier\nNo graph, fixed-point, or join search")
    box(ax,1.2,.35,2.1,.7,"Checked claims\nand diagnostics")
    arrow(ax,(2.08,2),(2.86,2))
    arrow(ax,(4.94,2),(5.69,2))
    arrow(ax,(6.8,1.65),(6.8,.73))
    ax.plot([1.1,1.1,4.1],[1.65,1.13,1.13],color="black",lw=.7)
    arrow(ax,(4.1,1.13),(4.1,.73))
    arrow(ax,(3.12,.35),(2.28,.35))
    save(fig,ax,out,"certificate-pipeline")
def properties(out):
    fig,ax=canvas((5.4,2.2),(-.5,3.1))
    box(ax,1.55,2.4,2.8,.60,"State confluence")
    box(ax,6.1,2.4,3,.60,"Unique terminal\nprogram identity")
    box(ax,1.55,.1,2.8,.65,"All reachable\nrewrites preserve")
    box(ax,6.1,.1,3,.65,"All terminal programs\nsource-equivalent")
    arrow(ax,(2.98,2.4),(4.56,2.4),"implies",(3.77,2.72))
    arrow(ax,(2.98,.1),(4.56,.1),"$⟦p_0⟧=⟦S⟧$",(3.77,.60))
    arrow(ax,(6.1,2.06),(6.1,.47),dash=True)
    ax.text(4.55,1.28,"Reachable preservation\nand initial source equivalence",
            ha="center",va="center",fontsize=8)
    save(fig,ax,out,"property-map")
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outdir",type=Path,default=HERE)
    args=ap.parse_args();args.outdir.mkdir(parents=True,exist_ok=True)
    diamond(args.outdir);commute(args.outdir);pipeline(args.outdir);properties(args.outdir)
    print("Four direct embedded-font vector schematics.")
if __name__=="__main__":main()
