import { convertPPTXToSlides, toPPTistTemplate } from './ppxtToSlides';
export async function importPPTXTemplate(arrayBuffer) {
    const { parse } = await import('pptxtojson');
    const json = await parse(arrayBuffer);
    const converted = convertPPTXToSlides(json, { fixedViewport: true });
    return toPPTistTemplate(converted);
}
