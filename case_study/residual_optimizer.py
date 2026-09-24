from __future__ import annotations
from dataclasses import dataclass
from collections import deque
from functools import lru_cache
from itertools import product
from typing import Iterable, Iterator, Mapping, Sequence
import random

@dataclass(frozen=True, slots=True)
class Expr:
    op: str
    args: tuple["Expr", ...] = ()
    value: int | str | None = None
    def __str__(self) -> str:
        if self.op == "const": return str(self.value)
        if self.op == "var": return str(self.value)
        symbol = "+" if self.op == "add" else "*"
        return f"({self.args[0]} {symbol} {self.args[1]})"
    def to_json(self):
        if self.op in {"const", "var"}: return {"op":self.op,"value":self.value}
        return {"op":self.op,"args":[a.to_json() for a in self.args]}

def Const(n:int)->Expr:return Expr("const",value=int(n))
def Var(n:str)->Expr:return Expr("var",value=n)
def Add(a:Expr,b:Expr)->Expr:return Expr("add",(a,b))
def Mul(a:Expr,b:Expr)->Expr:return Expr("mul",(a,b))

def size(e:Expr)->int:return 1+sum(size(a) for a in e.args)
def duplicate_adds(e:Expr)->int:return (1 if e.op=="add" and e.args[0]==e.args[1] else 0)+sum(duplicate_adds(a) for a in e.args)
def right_literal_twos(e:Expr)->int:return (1 if e.op=="mul" and e.args[1]==Const(2) and e.args[0]!=Const(2) else 0)+sum(right_literal_twos(a) for a in e.args)
def rank(e:Expr)->tuple[int,int,int]:
    # Each rewrite decreases this lexicographic rank. The first component handles
    # duplicate elimination even when Add(x,x) and Mul(2,x) have equal tree size.
    return (duplicate_adds(e), size(e), right_literal_twos(e))

def eval_expr(e:Expr, env:Mapping[str,int])->int:
    if e.op=="const":return int(e.value)
    if e.op=="var":return int(env[str(e.value)])
    a=eval_expr(e.args[0],env);b=eval_expr(e.args[1],env)
    return a+b if e.op=="add" else a*b

def _root_rewrites(e:Expr, mode:str)->list[tuple[str,Expr]]:
    out:list[tuple[str,Expr]]=[]
    if e.op not in {"add","mul"}:return out
    a,b=e.args
    if e.op=="add":
        if a.op=="const" and b.op=="const":out.append(("fold-add",Const(int(a.value)+int(b.value))))
        if b==Const(0):out.append(("add-zero-right",a))
        if a==Const(0):out.append(("add-zero-left",b))
        if a==b:
            if mode in {"buggy","left","canonical"}:out.append(("double-left",Mul(Const(2),a)))
            if mode in {"buggy","right"}:out.append(("double-right",Mul(a,Const(2))))
    else:
        if a.op=="const" and b.op=="const":out.append(("fold-mul",Const(int(a.value)*int(b.value))))
        if b==Const(1):out.append(("mul-one-right",a))
        if a==Const(1):out.append(("mul-one-left",b))
        if b==Const(0) or a==Const(0):out.append(("mul-zero",Const(0)))
        if mode=="canonical" and b==Const(2) and a!=Const(2):out.append(("orient-two-left",Mul(Const(2),a)))
    # Stable de-duplication guards against coincident arithmetic/identity rules.
    seen=set();ret=[]
    for rule,x in out:
        if x==e or x in seen:continue
        seen.add(x);ret.append((rule,x))
    return ret

def one_step(e:Expr, mode:str="buggy")->list[tuple[str,Expr]]:
    out=list(_root_rewrites(e,mode))
    for i,a in enumerate(e.args):
        for rule,a2 in one_step(a,mode):
            args=list(e.args);args[i]=a2
            out.append((f"arg{i}/{rule}",Expr(e.op,tuple(args),e.value)))
    seen=set();ret=[]
    for rule,x in out:
        if x in seen:continue
        if not rank(x)<rank(e):
            raise AssertionError(f"non-decreasing rewrite {rule}: {e} {rank(e)} -> {x} {rank(x)}")
        seen.add(x);ret.append((rule,x))
    return ret

def reachable_graph(start:Expr, mode:str="buggy", state_limit:int=100000):
    q=deque([start]);states={start};edges:dict[Expr,list[tuple[str,Expr]]]={}
    while q:
        e=q.popleft();succ=one_step(e,mode);edges[e]=succ
        for _,x in succ:
            if x not in states:
                states.add(x)
                if len(states)>state_limit:raise RuntimeError("state limit exceeded")
                q.append(x)
    return states,edges

def normal_forms(start:Expr, mode:str="buggy")->set[Expr]:
    states,edges=reachable_graph(start,mode)
    return {x for x in states if not edges[x]}

def paths_to_normal_forms(start:Expr, mode:str="buggy"):
    q=deque([start]);parent={start:None};edge_rule={}
    found={}
    while q:
        e=q.popleft();succ=one_step(e,mode)
        if not succ:found[e]=True
        for rule,x in succ:
            if x not in parent:parent[x]=e;edge_rule[x]=rule;q.append(x)
    ret={}
    for nf in found:
        cur=nf;rev=[]
        while parent[cur] is not None:
            rev.append({"rule":edge_rule[cur],"before":str(parent[cur]),"after":str(cur)})
            cur=parent[cur]
        ret[str(nf)]=list(reversed(rev))
    return ret

def semantic_signature(e:Expr, domain:Sequence[int]=(-2,-1,0,1,2))->tuple[int,...]:
    return tuple(eval_expr(e,{"x":x,"y":y}) for x,y in product(domain,repeat=2))

def generate_expressions(max_size:int=7, cap_per_size:int=2500)->list[Expr]:
    by:dict[int,list[Expr]]={1:[Const(0),Const(1),Const(2),Var("x"),Var("y")]}
    for n in range(3,max_size+1,2):
        vals=set()
        for l in range(1,n-1,2):
            r=n-1-l
            for a in by.get(l,[]):
                for b in by.get(r,[]):
                    vals.add(Add(a,b));vals.add(Mul(a,b))
                    if len(vals)>=cap_per_size:break
                if len(vals)>=cap_per_size:break
            if len(vals)>=cap_per_size:break
        by[n]=sorted(vals,key=str)[:cap_per_size]
    return [x for n in sorted(by) for x in by[n]]

def random_expr(rng:random.Random, depth:int)->Expr:
    if depth<=0 or rng.random()<0.24:return rng.choice([Const(0),Const(1),Const(2),Var("x"),Var("y")])
    op=Add if rng.random()<.5 else Mul
    # Deliberately include duplicated subtrees often enough to exercise the peak.
    a=random_expr(rng,depth-1)
    b=a if rng.random()<.22 else random_expr(rng,depth-1)
    return op(a,b)

def replay_path(start:Expr,path:list[dict],mode:str)->Expr:
    cur=start
    for item in path:
        candidates={(rule,str(nxt)):nxt for rule,nxt in one_step(cur,mode)}
        key=(item["rule"],item["after"])
        if item.get("before")!=str(cur) or key not in candidates:raise ValueError("invalid witness step")
        cur=candidates[key]
    return cur
