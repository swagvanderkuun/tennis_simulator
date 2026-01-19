'use client';

import { useEffect, useRef, useCallback } from 'react';
import * as d3 from 'd3';

interface BracketNode {
  id: number;
  round: string;
  matchIndex: number;
  player1Name?: string;
  player2Name?: string;
  player1Bye?: boolean;
  player2Bye?: boolean;
  player1Prob?: number;
  player2Prob?: number;
  winner?: string;
  children?: BracketNode[];
}

interface BracketTreeProps {
  data: BracketNode;
  width?: number;
  height?: number;
  onNodeClick?: (node: BracketNode) => void;
}

export function BracketTree({
  data,
  width = 1200,
  height = 800,
  onNodeClick,
}: BracketTreeProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  const renderBracket = useCallback(() => {
    if (!svgRef.current || !data) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const margin = { top: 40, right: 120, bottom: 40, left: 120 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const g = svg
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Create tree layout
    const treeLayout = d3.tree<BracketNode>().size([innerHeight, innerWidth]);

    // Create hierarchy
    const root = d3.hierarchy(data);
    const treeData = treeLayout(root);

    // Draw links
    g.selectAll('.link')
      .data(treeData.links())
      .enter()
      .append('path')
      .attr('class', 'link')
      .attr('fill', 'none')
      .attr('stroke', 'rgba(255, 255, 255, 0.1)')
      .attr('stroke-width', 2)
      .attr(
        'd',
        d3
          .linkHorizontal<d3.HierarchyPointLink<BracketNode>, d3.HierarchyPointNode<BracketNode>>()
          .x((d) => d.y)
          .y((d) => d.x)
      );

    // Draw nodes
    const nodes = g
      .selectAll('.node')
      .data(treeData.descendants())
      .enter()
      .append('g')
      .attr('class', 'node')
      .attr('transform', (d) => `translate(${d.y},${d.x})`)
      .style('cursor', 'pointer')
      .on('click', (event, d) => {
        if (onNodeClick) onNodeClick(d.data);
      });

    // Node background
    nodes
      .append('rect')
      .attr('x', -80)
      .attr('y', -30)
      .attr('width', 160)
      .attr('height', 60)
      .attr('rx', 8)
      .attr('fill', (d) =>
        d.data.winner ? 'rgba(56, 224, 124, 0.1)' : 'rgba(22, 31, 43, 0.9)'
      )
      .attr('stroke', (d) =>
        d.data.winner ? 'rgba(56, 224, 124, 0.5)' : 'rgba(255, 255, 255, 0.1)'
      )
      .attr('stroke-width', 1);

    // Player 1
    nodes
      .append('text')
      .attr('x', -70)
      .attr('y', -8)
      .attr('text-anchor', 'start')
      .attr('fill', (d) =>
        d.data.winner === d.data.player1Name ? '#38E07C' : '#E6EDF3'
      )
      .attr('font-size', '11px')
      .attr('font-family', 'var(--font-body)')
      .text((d) => {
        const name = d.data.player1Name || '';
        return name.length > 15 ? name.substring(0, 15) + '...' : name;
      });

    // Player 1 probability
    nodes
      .append('text')
      .attr('x', 70)
      .attr('y', -8)
      .attr('text-anchor', 'end')
      .attr('fill', '#9FB0C0')
      .attr('font-size', '10px')
      .attr('font-family', 'var(--font-mono)')
      .text((d) =>
        d.data.player1Prob !== undefined
          ? `${(d.data.player1Prob * 100).toFixed(0)}%`
          : ''
      );

    // Divider
    nodes
      .append('line')
      .attr('x1', -70)
      .attr('y1', 0)
      .attr('x2', 70)
      .attr('y2', 0)
      .attr('stroke', 'rgba(255, 255, 255, 0.1)')
      .attr('stroke-width', 1);

    // Player 2
    nodes
      .append('text')
      .attr('x', -70)
      .attr('y', 15)
      .attr('text-anchor', 'start')
      .attr('fill', (d) =>
        d.data.winner === d.data.player2Name ? '#38E07C' : '#E6EDF3'
      )
      .attr('font-size', '11px')
      .attr('font-family', 'var(--font-body)')
      .text((d) => {
        const name = d.data.player2Name || '';
        return name.length > 15 ? name.substring(0, 15) + '...' : name;
      });

    // Player 2 probability
    nodes
      .append('text')
      .attr('x', 70)
      .attr('y', 15)
      .attr('text-anchor', 'end')
      .attr('fill', '#9FB0C0')
      .attr('font-size', '10px')
      .attr('font-family', 'var(--font-mono)')
      .text((d) =>
        d.data.player2Prob !== undefined
          ? `${(d.data.player2Prob * 100).toFixed(0)}%`
          : ''
      );

    // Round label
    nodes
      .append('text')
      .attr('x', 0)
      .attr('y', -40)
      .attr('text-anchor', 'middle')
      .attr('fill', '#9FB0C0')
      .attr('font-size', '9px')
      .attr('font-family', 'var(--font-body)')
      .attr('text-transform', 'uppercase')
      .text((d) => d.data.round);
  }, [data, width, height, onNodeClick]);

  useEffect(() => {
    renderBracket();
  }, [renderBracket]);

  return (
    <div className="overflow-auto bg-surface rounded-xl border border-border">
      <svg
        ref={svgRef}
        width={width}
        height={height}
        className="block"
        style={{ minWidth: width }}
      />
    </div>
  );
}


