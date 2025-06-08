from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime

def gerar_pdf_orcamento(orcamento):
    """Gerar PDF do orçamento"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2c3e50')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.HexColor('#34495e')
    )
    
    normal_style = styles['Normal']
    normal_style.fontSize = 10
    
    # Conteúdo do PDF
    story = []
    
    # Cabeçalho
    story.append(Paragraph("LANTERCAR", title_style))
    story.append(Paragraph("Oficina Mecânica", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Título do documento
    story.append(Paragraph(f"ORÇAMENTO Nº {orcamento.numero_orcamento}", heading_style))
    story.append(Spacer(1, 20))
    
    # Informações do cliente e orçamento
    info_data = [
        ['Cliente:', orcamento.cliente.nome],
        ['CPF/CNPJ:', format_cpf_cnpj(orcamento.cliente.cpf_cnpj)],
        ['Telefone:', orcamento.cliente.telefone or 'Não informado'],
        ['Email:', orcamento.cliente.email or 'Não informado'],
        ['', ''],
        ['Data do Orçamento:', orcamento.data_orcamento.strftime('%d/%m/%Y')],
        ['Válido até:', orcamento.validade.strftime('%d/%m/%Y')],
        ['Responsável:', orcamento.usuario.nome],
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # Descrição do serviço
    story.append(Paragraph("DESCRIÇÃO DO SERVIÇO", heading_style))
    story.append(Paragraph(orcamento.descricao_servico, normal_style))
    story.append(Spacer(1, 20))
    
    # Itens do orçamento
    if orcamento.itens:
        story.append(Paragraph("MATERIAIS", heading_style))
        
        # Cabeçalho da tabela
        items_data = [['Item', 'Código', 'Descrição', 'Qtd', 'Unid', 'Valor Unit.', 'Subtotal']]
        
        # Itens
        for i, item in enumerate(orcamento.itens, 1):
            items_data.append([
                str(i),
                item.material.codigo,
                item.material.nome,
                f"{item.quantidade:.2f}".replace('.', ','),
                item.material.unidade_medida,
                f"R$ {item.preco_unitario:.2f}".replace('.', ','),
                f"R$ {item.subtotal:.2f}".replace('.', ',')
            ])
        
        items_table = Table(items_data, colWidths=[0.5*inch, 1*inch, 2.5*inch, 0.7*inch, 0.5*inch, 1*inch, 1*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(items_table)
        story.append(Spacer(1, 20))
    
    # Resumo financeiro
    story.append(Paragraph("RESUMO FINANCEIRO", heading_style))
    
    total_materiais = sum(item.subtotal for item in orcamento.itens)
    
    resumo_data = [
        ['Subtotal Materiais:', f"R$ {total_materiais:.2f}".replace('.', ',')],
        ['Mão de Obra:', f"R$ {orcamento.valor_mao_obra:.2f}".replace('.', ',')],
        ['TOTAL GERAL:', f"R$ {orcamento.valor_total:.2f}".replace('.', ',')]
    ]
    
    resumo_table = Table(resumo_data, colWidths=[4*inch, 2*inch])
    resumo_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 14),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LINEBELOW', (0, -1), (-1, -1), 2, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(resumo_table)
    story.append(Spacer(1, 30))
    
    # Observações
    if orcamento.observacoes:
        story.append(Paragraph("OBSERVAÇÕES", heading_style))
        story.append(Paragraph(orcamento.observacoes, normal_style))
        story.append(Spacer(1, 20))
    
    # Termos e condições
    story.append(Paragraph("TERMOS E CONDIÇÕES", heading_style))
    termos = """
    1. Este orçamento tem validade até a data especificada acima.
    2. Os preços estão sujeitos a alteração sem aviso prévio.
    3. O serviço será executado conforme descrito neste orçamento.
    4. Materiais não utilizados poderão ser devolvidos mediante acordo.
    5. O pagamento deverá ser efetuado conforme combinado.
    """
    story.append(Paragraph(termos, normal_style))
    story.append(Spacer(1, 30))
    
    # Assinaturas
    story.append(Paragraph("ASSINATURAS", heading_style))
    story.append(Spacer(1, 40))
    
    assinaturas_data = [
        ['_' * 30, '_' * 30],
        ['Cliente', 'Lantercar'],
        [orcamento.cliente.nome, orcamento.usuario.nome]
    ]
    
    assinaturas_table = Table(assinaturas_data, colWidths=[3*inch, 3*inch])
    assinaturas_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 1), (-1, -1), 10),
    ]))
    
    story.append(assinaturas_table)
    
    # Rodapé
    story.append(Spacer(1, 30))
    rodape = f"Documento gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}"
    story.append(Paragraph(rodape, ParagraphStyle('Footer', parent=normal_style, fontSize=8, alignment=TA_CENTER)))
    
    # Gerar PDF
    doc.build(story)
    
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content

def format_cpf_cnpj(cpf_cnpj):
    """Formatar CPF/CNPJ para exibição"""
    if not cpf_cnpj:
        return ''
    
    cpf_cnpj = ''.join(filter(str.isdigit, cpf_cnpj))
    
    if len(cpf_cnpj) == 11:  # CPF
        return f'{cpf_cnpj[:3]}.{cpf_cnpj[3:6]}.{cpf_cnpj[6:9]}-{cpf_cnpj[9:]}'
    elif len(cpf_cnpj) == 14:  # CNPJ
        return f'{cpf_cnpj[:2]}.{cpf_cnpj[2:5]}.{cpf_cnpj[5:8]}/{cpf_cnpj[8:12]}-{cpf_cnpj[12:]}'
    else:
        return cpf_cnpj



def gerar_pdf_contrato(contrato):
    """Gerar PDF do contrato"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2c3e50')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.HexColor('#34495e')
    )
    
    normal_style = styles['Normal']
    normal_style.fontSize = 10
    
    # Conteúdo do PDF
    story = []
    
    # Cabeçalho
    story.append(Paragraph("LANTERCAR", title_style))
    story.append(Paragraph("Oficina Mecânica", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Título do documento
    story.append(Paragraph(f"CONTRATO DE PRESTAÇÃO DE SERVIÇOS Nº {contrato.numero_contrato}", heading_style))
    story.append(Spacer(1, 20))
    
    # Informações das partes
    ordem = contrato.ordem_servico
    orcamento = ordem.orcamento
    cliente = orcamento.cliente
    
    story.append(Paragraph("CONTRATANTE", heading_style))
    contratante_info = f"""
    <b>Nome:</b> {cliente.nome}<br/>
    <b>CPF/CNPJ:</b> {format_cpf_cnpj(cliente.cpf_cnpj)}<br/>
    <b>Telefone:</b> {cliente.telefone or 'Não informado'}<br/>
    <b>Email:</b> {cliente.email or 'Não informado'}<br/>
    <b>Endereço:</b> {cliente.endereco or 'Não informado'}
    """
    story.append(Paragraph(contratante_info, normal_style))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("CONTRATADA", heading_style))
    contratada_info = """
    <b>Razão Social:</b> LANTERCAR - Oficina Mecânica<br/>
    <b>Responsável:</b> Rodrigo<br/>
    <b>Telefone:</b> (11) 99999-9999<br/>
    <b>Email:</b> contato@lantercar.com
    """
    story.append(Paragraph(contratada_info, normal_style))
    story.append(Spacer(1, 20))
    
    # Dados do contrato
    story.append(Paragraph("DADOS DO CONTRATO", heading_style))
    dados_contrato = [
        ['Número do Contrato:', contrato.numero_contrato],
        ['Data do Contrato:', contrato.data_contrato.strftime('%d/%m/%Y')],
        ['Ordem de Serviço:', ordem.numero_ordem],
        ['Orçamento Base:', orcamento.numero_orcamento],
        ['Valor Total:', f"R$ {orcamento.valor_total:.2f}".replace('.', ',')],
        ['Status:', contrato.status.title()]
    ]
    
    dados_table = Table(dados_contrato, colWidths=[2.5*inch, 3.5*inch])
    dados_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    story.append(dados_table)
    story.append(Spacer(1, 20))
    
    # Objeto do contrato
    story.append(Paragraph("OBJETO DO CONTRATO", heading_style))
    story.append(Paragraph(orcamento.descricao_servico, normal_style))
    story.append(Spacer(1, 20))
    
    # Termos e condições
    story.append(Paragraph("TERMOS E CONDIÇÕES", heading_style))
    story.append(Paragraph(contrato.termos_condicoes, normal_style))
    story.append(Spacer(1, 30))
    
    # Assinaturas
    story.append(Paragraph("ASSINATURAS", heading_style))
    story.append(Spacer(1, 40))
    
    assinaturas_data = [
        ['_' * 30, '_' * 30],
        ['CONTRATANTE', 'CONTRATADA'],
        [cliente.nome, 'LANTERCAR - Oficina Mecânica']
    ]
    
    assinaturas_table = Table(assinaturas_data, colWidths=[3*inch, 3*inch])
    assinaturas_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 1), (-1, -1), 10),
    ]))
    
    story.append(assinaturas_table)
    
    # Rodapé
    story.append(Spacer(1, 30))
    rodape = f"Documento gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}"
    story.append(Paragraph(rodape, ParagraphStyle('Footer', parent=normal_style, fontSize=8, alignment=TA_CENTER)))
    
    # Gerar PDF
    doc.build(story)
    
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content

def gerar_pdf_ordem_servico(ordem):
    """Gerar PDF da ordem de serviço"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2c3e50')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.HexColor('#34495e')
    )
    
    normal_style = styles['Normal']
    normal_style.fontSize = 10
    
    # Conteúdo do PDF
    story = []
    
    # Cabeçalho
    story.append(Paragraph("LANTERCAR", title_style))
    story.append(Paragraph("Oficina Mecânica", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Título do documento
    story.append(Paragraph(f"ORDEM DE SERVIÇO Nº {ordem.numero_ordem}", heading_style))
    story.append(Spacer(1, 20))
    
    # Informações da ordem
    orcamento = ordem.orcamento
    cliente = orcamento.cliente
    
    info_data = [
        ['Cliente:', cliente.nome],
        ['CPF/CNPJ:', format_cpf_cnpj(cliente.cpf_cnpj)],
        ['Telefone:', cliente.telefone or 'Não informado'],
        ['Email:', cliente.email or 'Não informado'],
        ['', ''],
        ['Orçamento Base:', orcamento.numero_orcamento],
        ['Data de Início:', ordem.data_inicio.strftime('%d/%m/%Y %H:%M')],
        ['Data de Conclusão:', ordem.data_conclusao.strftime('%d/%m/%Y %H:%M') if ordem.data_conclusao else 'Em andamento'],
        ['Status:', ordem.status.replace('_', ' ').title()],
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # Descrição do serviço
    story.append(Paragraph("DESCRIÇÃO DO SERVIÇO", heading_style))
    story.append(Paragraph(orcamento.descricao_servico, normal_style))
    story.append(Spacer(1, 20))
    
    # Materiais utilizados
    if orcamento.itens:
        story.append(Paragraph("MATERIAIS UTILIZADOS", heading_style))
        
        # Cabeçalho da tabela
        items_data = [['Item', 'Código', 'Descrição', 'Qtd', 'Unid', 'Valor Unit.', 'Subtotal']]
        
        # Itens
        for i, item in enumerate(orcamento.itens, 1):
            items_data.append([
                str(i),
                item.material.codigo,
                item.material.nome,
                f"{item.quantidade:.2f}".replace('.', ','),
                item.material.unidade_medida,
                f"R$ {item.preco_unitario:.2f}".replace('.', ','),
                f"R$ {item.subtotal:.2f}".replace('.', ',')
            ])
        
        items_table = Table(items_data, colWidths=[0.5*inch, 1*inch, 2.5*inch, 0.7*inch, 0.5*inch, 1*inch, 1*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(items_table)
        story.append(Spacer(1, 20))
    
    # Resumo financeiro
    story.append(Paragraph("RESUMO FINANCEIRO", heading_style))
    
    total_materiais = sum(item.subtotal for item in orcamento.itens)
    
    resumo_data = [
        ['Subtotal Materiais:', f"R$ {total_materiais:.2f}".replace('.', ',')],
        ['Mão de Obra:', f"R$ {orcamento.valor_mao_obra:.2f}".replace('.', ',')],
        ['TOTAL GERAL:', f"R$ {orcamento.valor_total:.2f}".replace('.', ',')]
    ]
    
    resumo_table = Table(resumo_data, colWidths=[4*inch, 2*inch])
    resumo_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 14),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LINEBELOW', (0, -1), (-1, -1), 2, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(resumo_table)
    story.append(Spacer(1, 20))
    
    # Observações
    if ordem.observacoes:
        story.append(Paragraph("OBSERVAÇÕES", heading_style))
        story.append(Paragraph(ordem.observacoes, normal_style))
        story.append(Spacer(1, 20))
    
    # Assinatura do cliente
    story.append(Paragraph("ASSINATURA DO CLIENTE", heading_style))
    story.append(Spacer(1, 40))
    
    assinatura_data = [
        ['_' * 40],
        [cliente.nome],
        ['Cliente']
    ]
    
    assinatura_table = Table(assinatura_data, colWidths=[4*inch])
    assinatura_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 1), (-1, -1), 10),
    ]))
    
    story.append(assinatura_table)
    
    # Rodapé
    story.append(Spacer(1, 30))
    rodape = f"Documento gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}"
    story.append(Paragraph(rodape, ParagraphStyle('Footer', parent=normal_style, fontSize=8, alignment=TA_CENTER)))
    
    # Gerar PDF
    doc.build(story)
    
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content


def gerar_pdf_nota_fiscal(nota_fiscal):
    """Gerar PDF da nota fiscal"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2c3e50')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.HexColor('#34495e')
    )
    
    normal_style = styles['Normal']
    normal_style.fontSize = 10
    
    # Conteúdo do PDF
    story = []
    
    # Cabeçalho
    story.append(Paragraph("LANTERCAR", title_style))
    story.append(Paragraph("Oficina Mecânica", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Título do documento
    story.append(Paragraph(f"NOTA FISCAL DE SERVIÇOS Nº {nota_fiscal.numero_nf}", heading_style))
    story.append(Spacer(1, 20))
    
    # Informações da nota fiscal
    ordem = nota_fiscal.ordem_servico
    orcamento = ordem.orcamento
    cliente = orcamento.cliente
    
    # Dados da empresa
    story.append(Paragraph("PRESTADOR DE SERVIÇOS", heading_style))
    prestador_info = """
    <b>Razão Social:</b> LANTERCAR - Oficina Mecânica<br/>
    <b>CNPJ:</b> 00.000.000/0001-00<br/>
    <b>Inscrição Municipal:</b> 123456789<br/>
    <b>Endereço:</b> Rua das Oficinas, 123 - Centro<br/>
    <b>Cidade:</b> São Paulo - SP - CEP: 01000-000<br/>
    <b>Telefone:</b> (11) 99999-9999
    """
    story.append(Paragraph(prestador_info, normal_style))
    story.append(Spacer(1, 15))
    
    # Dados do cliente
    story.append(Paragraph("TOMADOR DE SERVIÇOS", heading_style))
    tomador_info = f"""
    <b>Nome/Razão Social:</b> {cliente.nome}<br/>
    <b>CPF/CNPJ:</b> {format_cpf_cnpj(cliente.cpf_cnpj)}<br/>
    <b>Telefone:</b> {cliente.telefone or 'Não informado'}<br/>
    <b>Email:</b> {cliente.email or 'Não informado'}<br/>
    <b>Endereço:</b> {cliente.endereco or 'Não informado'}<br/>
    <b>Cidade:</b> {cliente.cidade or 'Não informado'} - {cliente.estado or ''} - CEP: {cliente.cep or 'Não informado'}
    """
    story.append(Paragraph(tomador_info, normal_style))
    story.append(Spacer(1, 20))
    
    # Dados da nota fiscal
    story.append(Paragraph("DADOS DA NOTA FISCAL", heading_style))
    dados_nf = [
        ['Número da NF:', nota_fiscal.numero_nf],
        ['Data de Emissão:', nota_fiscal.data_emissao.strftime('%d/%m/%Y')],
        ['Ordem de Serviço:', ordem.numero_ordem],
        ['Orçamento Base:', orcamento.numero_orcamento],
        ['Status:', nota_fiscal.status.title()]
    ]
    
    dados_table = Table(dados_nf, colWidths=[2.5*inch, 3.5*inch])
    dados_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    story.append(dados_table)
    story.append(Spacer(1, 20))
    
    # Descrição dos serviços
    story.append(Paragraph("DISCRIMINAÇÃO DOS SERVIÇOS", heading_style))
    
    # Serviço principal
    servicos_data = [['Item', 'Descrição', 'Quantidade', 'Valor Unitário', 'Valor Total']]
    
    # Mão de obra
    if orcamento.valor_mao_obra > 0:
        servicos_data.append([
            '1',
            orcamento.descricao_servico,
            '1',
            f"R$ {orcamento.valor_mao_obra:.2f}".replace('.', ','),
            f"R$ {orcamento.valor_mao_obra:.2f}".replace('.', ',')
        ])
    
    # Materiais (agrupados)
    if orcamento.itens:
        total_materiais = sum(item.subtotal for item in orcamento.itens)
        item_num = 2 if orcamento.valor_mao_obra > 0 else 1
        
        materiais_desc = "Materiais utilizados: " + ", ".join([f"{item.material.nome} ({item.quantidade:.2f} {item.material.unidade_medida})" for item in orcamento.itens])
        
        servicos_data.append([
            str(item_num),
            materiais_desc,
            '1',
            f"R$ {total_materiais:.2f}".replace('.', ','),
            f"R$ {total_materiais:.2f}".replace('.', ',')
        ])
    
    servicos_table = Table(servicos_data, colWidths=[0.5*inch, 3.5*inch, 1*inch, 1.2*inch, 1.2*inch])
    servicos_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(servicos_table)
    story.append(Spacer(1, 20))
    
    # Resumo dos valores
    story.append(Paragraph("RESUMO DOS VALORES", heading_style))
    
    resumo_valores = [
        ['Valor Total dos Serviços:', f"R$ {nota_fiscal.valor_total:.2f}".replace('.', ',')],
        ['(-) Deduções:', 'R$ 0,00'],
        ['Base de Cálculo:', f"R$ {nota_fiscal.valor_total:.2f}".replace('.', ',')],
        ['Alíquota ISS:', '5,00%'],
        ['Valor do ISS:', f"R$ {(nota_fiscal.valor_total * 0.05):.2f}".replace('.', ',')],
        ['Valor Líquido:', f"R$ {(nota_fiscal.valor_total - (nota_fiscal.valor_total * 0.05)):.2f}".replace('.', ',')]
    ]
    
    resumo_table = Table(resumo_valores, colWidths=[4*inch, 2*inch])
    resumo_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LINEBELOW', (0, -1), (-1, -1), 2, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(resumo_table)
    story.append(Spacer(1, 30))
    
    # Informações adicionais
    story.append(Paragraph("INFORMAÇÕES ADICIONAIS", heading_style))
    info_adicional = """
    Esta nota fiscal refere-se aos serviços de oficina mecânica prestados conforme ordem de serviço especificada.
    
    Tributos: ISS retido na fonte conforme legislação municipal vigente.
    
    Esta nota fiscal foi gerada eletronicamente pelo sistema de gestão LANTERCAR.
    """
    story.append(Paragraph(info_adicional, normal_style))
    story.append(Spacer(1, 20))
    
    # Rodapé
    rodape = f"Nota Fiscal gerada em {datetime.now().strftime('%d/%m/%Y às %H:%M')}"
    story.append(Paragraph(rodape, ParagraphStyle('Footer', parent=normal_style, fontSize=8, alignment=TA_CENTER)))
    
    # Gerar PDF
    doc.build(story)
    
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content


def gerar_pdf_relatorio_servicos(ordens, filtros):
    """Gerar PDF do relatório de serviços"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2c3e50')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.HexColor('#34495e')
    )
    
    normal_style = styles['Normal']
    normal_style.fontSize = 10
    
    # Conteúdo do PDF
    story = []
    
    # Cabeçalho
    story.append(Paragraph("LANTERCAR", title_style))
    story.append(Paragraph("Oficina Mecânica", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Título do documento
    story.append(Paragraph("RELATÓRIO DE SERVIÇOS", heading_style))
    story.append(Spacer(1, 20))
    
    # Filtros aplicados
    story.append(Paragraph("FILTROS APLICADOS", heading_style))
    filtros_info = []
    
    if filtros.get('data_inicio'):
        filtros_info.append(f"Data Início: {datetime.strptime(filtros['data_inicio'], '%Y-%m-%d').strftime('%d/%m/%Y')}")
    
    if filtros.get('data_fim'):
        filtros_info.append(f"Data Fim: {datetime.strptime(filtros['data_fim'], '%Y-%m-%d').strftime('%d/%m/%Y')}")
    
    if filtros.get('status'):
        filtros_info.append(f"Status: {filtros['status'].replace('_', ' ').title()}")
    
    if filtros.get('cliente_id'):
        # Buscar nome do cliente
        from src.models import Cliente
        cliente = Cliente.query.get(filtros['cliente_id'])
        if cliente:
            filtros_info.append(f"Cliente: {cliente.nome}")
    
    if not filtros_info:
        filtros_info.append("Nenhum filtro aplicado")
    
    for filtro in filtros_info:
        story.append(Paragraph(filtro, normal_style))
    
    story.append(Spacer(1, 20))
    
    # Estatísticas
    story.append(Paragraph("RESUMO ESTATÍSTICO", heading_style))
    
    total_servicos = len(ordens)
    valor_total = sum(ordem.orcamento.valor_total for ordem in ordens)
    servicos_concluidos = len([o for o in ordens if o.status == 'concluido'])
    servicos_em_andamento = len([o for o in ordens if o.status == 'em_andamento'])
    servicos_cancelados = len([o for o in ordens if o.status == 'cancelado'])
    
    estatisticas_data = [
        ['Total de Serviços:', str(total_servicos)],
        ['Valor Total:', f"R$ {valor_total:.2f}".replace('.', ',')],
        ['Serviços Concluídos:', str(servicos_concluidos)],
        ['Serviços em Andamento:', str(servicos_em_andamento)],
        ['Serviços Cancelados:', str(servicos_cancelados)]
    ]
    
    estatisticas_table = Table(estatisticas_data, colWidths=[3*inch, 2*inch])
    estatisticas_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    story.append(estatisticas_table)
    story.append(Spacer(1, 20))
    
    # Lista de serviços
    if ordens:
        story.append(Paragraph("DETALHAMENTO DOS SERVIÇOS", heading_style))
        
        # Cabeçalho da tabela
        servicos_data = [['OS', 'Cliente', 'Data Início', 'Status', 'Valor']]
        
        # Serviços
        for ordem in ordens:
            servicos_data.append([
                ordem.numero_ordem,
                ordem.orcamento.cliente.nome[:20] + '...' if len(ordem.orcamento.cliente.nome) > 20 else ordem.orcamento.cliente.nome,
                ordem.data_inicio.strftime('%d/%m/%Y'),
                ordem.status.replace('_', ' ').title(),
                f"R$ {ordem.orcamento.valor_total:.2f}".replace('.', ',')
            ])
        
        servicos_table = Table(servicos_data, colWidths=[1.2*inch, 2.5*inch, 1*inch, 1.3*inch, 1*inch])
        servicos_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(servicos_table)
    else:
        story.append(Paragraph("Nenhum serviço encontrado com os filtros aplicados.", normal_style))
    
    story.append(Spacer(1, 30))
    
    # Rodapé
    rodape = f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}"
    story.append(Paragraph(rodape, ParagraphStyle('Footer', parent=normal_style, fontSize=8, alignment=TA_CENTER)))
    
    # Gerar PDF
    doc.build(story)
    
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content

