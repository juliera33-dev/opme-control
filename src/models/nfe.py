from ..extensions import db

class NFeHeader(db.Model):
    __tablename__ = 'nfe_header'
    id = db.Column(db.Integer, primary_key=True)
    nNF = db.Column(db.String(20), nullable=False)
    dEmi = db.Column(db.Date, nullable=False)
    CNPJ_emit = db.Column(db.String(14), nullable=False)
    xNome_emit = db.Column(db.String(100), nullable=False)
    CNPJ_dest = db.Column(db.String(14), nullable=False)
    xNome_dest = db.Column(db.String(100), nullable=False)

class NFeItem(db.Model):
    __tablename__ = 'nfe_item'
    id = db.Column(db.Integer, primary_key=True)
    nfe_header_id = db.Column(db.Integer, db.ForeignKey('nfe_header.id'), nullable=False)
    cProd = db.Column(db.String(20), nullable=False)
    xProd = db.Column(db.String(100), nullable=False)
    CFOP = db.Column(db.String(4), nullable=False)
    uCom = db.Column(db.String(10), nullable=False)
    qCom = db.Column(db.Float, nullable=False)
    vUnCom = db.Column(db.Float, nullable=False)
    nLote = db.Column(db.String(20))
    qLote = db.Column(db.Float)

class EstoqueConsignacao(db.Model):
    __tablename__ = 'estoque_consignacao'
    id = db.Column(db.Integer, primary_key=True)
    produto = db.Column(db.String(100), nullable=False)
    quantidade = db.Column(db.Float, nullable=False, default=0.0)
    nfe_item_id = db.Column(db.Integer, db.ForeignKey('nfe_item.id'))
